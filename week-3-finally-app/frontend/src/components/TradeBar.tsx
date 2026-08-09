'use client';

import React, { useState, useEffect } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { ShoppingCart, ArrowDownRight, ArrowUpRight } from 'lucide-react';

export const TradeBar: React.FC = () => {
  const { selectedTicker, executeTrade, portfolio } = useTerminalStore();

  const [ticker, setTicker] = useState(selectedTicker);
  const [quantity, setQuantity] = useState<number>(1);
  const [orderType, setOrderType] = useState<'MARKET'>('MARKET');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    setTicker(selectedTicker);
  }, [selectedTicker]);

  const handleTrade = async (side: 'buy' | 'sell') => {
    if (!ticker.trim() || quantity <= 0) {
      setErrorMessage('Please enter a valid ticker and quantity > 0');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await executeTrade(ticker.trim().toUpperCase(), side, Number(quantity));
      setSuccessMessage(`Market ${side.toUpperCase()} order executed for ${quantity} sh of ${ticker.toUpperCase()}`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage(err.message || 'Trade execution failed');
      setTimeout(() => setErrorMessage(null), 4000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col justify-between h-full">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <ShoppingCart className="w-4 h-4 text-terminal-yellow" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-terminal-yellow">
            Order Entry Trade Bar
          </h2>
        </div>
        <span className="text-[10px] font-mono text-terminal-muted">
          Available Cash: ${portfolio ? portfolio.cash_balance.toFixed(2) : '10,000.00'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 items-center">
        {/* Ticker Input */}
        <div>
          <label className="block text-[10px] uppercase text-terminal-muted mb-0.5">Ticker</label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            className="w-full px-2 py-1 text-xs font-mono bg-terminal-bg border border-terminal-border rounded text-white focus:outline-none focus:border-terminal-blue uppercase"
            placeholder="TICKER"
          />
        </div>

        {/* Quantity Input */}
        <div>
          <label className="block text-[10px] uppercase text-terminal-muted mb-0.5">Quantity</label>
          <input
            type="number"
            min="1"
            value={quantity}
            onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
            className="w-full px-2 py-1 text-xs font-mono bg-terminal-bg border border-terminal-border rounded text-white focus:outline-none focus:border-terminal-blue"
          />
        </div>

        {/* Order Type */}
        <div>
          <label className="block text-[10px] uppercase text-terminal-muted mb-0.5">Order Type</label>
          <select
            value={orderType}
            onChange={(e) => setOrderType(e.target.value as 'MARKET')}
            className="w-full px-2 py-1 text-xs font-mono bg-terminal-bg border border-terminal-border rounded text-white focus:outline-none focus:border-terminal-blue"
          >
            <option value="MARKET">MARKET</option>
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-1.5 pt-3">
          <button
            onClick={() => handleTrade('buy')}
            disabled={isSubmitting}
            className="flex-1 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold rounded flex items-center justify-center space-x-1 transition disabled:opacity-50"
          >
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>BUY</span>
          </button>
          <button
            onClick={() => handleTrade('sell')}
            disabled={isSubmitting}
            className="flex-1 py-1.5 bg-red-600 hover:bg-red-500 text-white font-mono text-xs font-bold rounded flex items-center justify-center space-x-1 transition disabled:opacity-50"
          >
            <ArrowDownRight className="w-3.5 h-3.5" />
            <span>SELL</span>
          </button>
        </div>
      </div>

      {/* Error & Success Toasts */}
      {(errorMessage || successMessage) && (
        <div className="mt-2">
          {errorMessage && (
            <p className="text-[10px] font-mono text-red-400 bg-red-500/10 border border-red-500/30 px-2 py-0.5 rounded">
              {errorMessage}
            </p>
          )}
          {successMessage && (
            <p className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
              {successMessage}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
