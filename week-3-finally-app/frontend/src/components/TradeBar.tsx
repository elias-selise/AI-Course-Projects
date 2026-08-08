import React, { useState, useEffect } from 'react';
import { Side, TickerData, Portfolio } from '../types';
import { ArrowLeftRight, CheckCircle, AlertTriangle } from 'lucide-react';

interface TradeBarProps {
  selectedTicker: string;
  watchlist: TickerData[];
  portfolio: Portfolio;
  onExecuteTrade: (ticker: string, quantity: number, side: Side) => Promise<{ success: boolean; message: string }>;
}

export const TradeBar: React.FC<TradeBarProps> = ({
  selectedTicker,
  watchlist,
  portfolio,
  onExecuteTrade,
}) => {
  const [ticker, setTicker] = useState(selectedTicker || 'AAPL');
  const [side, setSide] = useState<Side>('buy');
  const [quantity, setQuantity] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    if (selectedTicker) {
      setTicker(selectedTicker);
    }
  }, [selectedTicker]);

  const currentPrice = watchlist.find(t => t.ticker === ticker.toUpperCase())?.price || 150.0;
  const totalCost = currentPrice * (quantity || 0);

  // Position held for this ticker
  const position = portfolio.positions.find(p => p.ticker === ticker.toUpperCase());
  const ownedQty = position?.quantity || 0;

  const handleQuickQty = (qty: number | 'MAX') => {
    if (qty === 'MAX') {
      if (side === 'buy') {
        const maxBuy = Math.floor(portfolio.cash_balance / currentPrice);
        setQuantity(Math.max(1, maxBuy));
      } else {
        setQuantity(Math.max(1, ownedQty));
      }
    } else {
      setQuantity(qty);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim() || quantity <= 0) return;

    setIsSubmitting(true);
    setToast(null);

    const result = await onExecuteTrade(ticker.trim().toUpperCase(), quantity, side);

    setIsSubmitting(false);

    if (result.success) {
      setToast({ type: 'success', message: result.message });
    } else {
      setToast({ type: 'error', message: result.message });
    }

    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  return (
    <div className="bg-panel border border-border rounded p-3 select-none font-mono">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <ArrowLeftRight className="w-4 h-4 text-accent-yellow" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-accent-yellow">
            INSTANT TRADE EXECUTION BAR
          </h2>
        </div>
        
        <div className="text-[11px] text-gray-400">
          {side === 'buy' ? (
            <span>Avail Cash: <strong className="text-white">${portfolio.cash_balance.toFixed(2)}</strong></span>
          ) : (
            <span>Position Held: <strong className="text-white">{ownedQty} shares</strong></span>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-wrap items-center gap-3">
        {/* Side Selector (BUY / SELL Toggle) */}
        <div className="flex rounded bg-black/50 p-1 border border-border">
          <button
            type="button"
            data-testid="buy-button"
            onClick={() => setSide('buy')}
            className={`px-3 py-1 text-xs font-bold rounded transition-colors ${
              side === 'buy'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            BUY
          </button>
          <button
            type="button"
            data-testid="sell-button"
            onClick={() => setSide('sell')}
            className={`px-3 py-1 text-xs font-bold rounded transition-colors ${
              side === 'sell'
                ? 'bg-rose-600 text-white shadow'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            SELL
          </button>
        </div>

        {/* Ticker Input */}
        <div className="flex flex-col">
          <label className="text-[10px] text-gray-400 mb-0.5">SYMBOL</label>
          <input
            type="text"
            data-testid="trade-ticker-input"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="TICKER"
            className="w-24 px-2 py-1 bg-black/60 border border-border rounded text-xs font-bold text-white uppercase focus:outline-none focus:border-accent-blue"
          />
        </div>

        {/* Quantity Input & Preset Buttons */}
        <div className="flex flex-col">
          <label className="text-[10px] text-gray-400 mb-0.5">QUANTITY</label>
          <div className="flex items-center gap-1">
            <input
              type="number"
              data-testid="trade-quantity-input"
              min="1"
              step="1"
              value={quantity || ''}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 0))}
              className="w-20 px-2 py-1 bg-black/60 border border-border rounded text-xs font-bold text-white focus:outline-none focus:border-accent-blue"
            />
            <div className="flex items-center gap-0.5">
              {[1, 5, 10, 'MAX'].map((preset) => (
                <button
                  key={preset.toString()}
                  type="button"
                  onClick={() => handleQuickQty(preset as any)}
                  className="px-1.5 py-0.5 rounded bg-gray-800 text-[10px] text-gray-300 hover:bg-gray-700 border border-border"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Estimated Order Cost */}
        <div className="flex flex-col min-w-[120px]">
          <label className="text-[10px] text-gray-400 mb-0.5">EST. ORDER VALUE</label>
          <div className="text-xs font-bold text-accent-yellow py-1">
            ${totalCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span className="text-[10px] text-gray-500 font-normal ml-1">(@ ${(currentPrice ?? 0).toFixed(2)})</span>
          </div>
        </div>

        {/* Submit Execution Button */}
        <button
          type="submit"
          data-testid="execute-trade-button"
          disabled={isSubmitting || quantity <= 0}
          className={`ml-auto px-5 py-2 rounded text-xs font-bold font-mono tracking-wider transition-all flex items-center gap-2 ${
            side === 'buy'
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30'
              : 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/30'
          } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isSubmitting ? (
            <span className="animate-spin">⏳</span>
          ) : (
            <span>EXECUTE {side.toUpperCase()} {quantity} {ticker}</span>
          )}
        </button>
      </form>

      {/* Execution Toast / Banner */}
      {toast && (
        <div
          className={`mt-2.5 px-3 py-1.5 rounded text-xs flex items-center gap-2 border font-mono animate-pulse ${
            toast.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
              : 'bg-rose-950/80 border-rose-500 text-rose-300'
          }`}
        >
          {toast.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
};
