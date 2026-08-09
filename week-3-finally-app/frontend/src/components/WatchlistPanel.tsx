import React, { useState } from 'react';
import { TickerData } from '../types';
import { Plus, Trash2, TrendingUp, TrendingDown, Eye } from 'lucide-react';

interface WatchlistPanelProps {
  watchlist: TickerData[];
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
  onAddTicker: (ticker: string) => void;
  onRemoveTicker: (ticker: string) => void;
  flashMap?: Record<string, 'up' | 'down'>;
}

// Sparkline SVG helper
const Sparkline: React.FC<{ data: number[]; isUp: boolean }> = ({ data, isUp }) => {
  if (!data || data.length < 2) {
    return <div className="w-16 h-6 bg-gray-800/40 rounded animate-pulse" />;
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const width = 64;
  const height = 24;

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * (height - 4) - 2;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  const strokeColor = isUp ? '#22c55e' : '#ef4444';

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
};

export const WatchlistPanel: React.FC<WatchlistPanelProps> = ({
  watchlist,
  selectedTicker,
  onSelectTicker,
  onAddTicker,
  onRemoveTicker,
  flashMap = {},
}) => {
  const [newTickerInput, setNewTickerInput] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTickerInput.trim()) return;
    const symbol = newTickerInput.trim().toUpperCase();
    if (watchlist.some(t => t.ticker === symbol)) {
      setErrorMsg(`${symbol} is already in watchlist`);
      setTimeout(() => setErrorMsg(''), 2500);
      return;
    }
    onAddTicker(symbol);
    setNewTickerInput('');
    setErrorMsg('');
  };

  return (
    <div data-testid="watchlist-panel" className="bg-panel border border-border rounded flex flex-col h-full overflow-hidden select-none">
      {/* Panel Header */}
      <div className="bg-panel-header px-3.5 py-2.5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-accent-yellow" />
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-accent-yellow">
            WATCHLIST ({watchlist.length})
          </h2>
        </div>
        
        {/* Add Ticker Form */}
        <form onSubmit={handleAddSubmit} className="flex items-center gap-1.5">
          <input
            type="text"
            data-testid="add-ticker-input"
            placeholder="ADD TICKER"
            value={newTickerInput}
            onChange={(e) => setNewTickerInput(e.target.value)}
            className="w-20 px-2 py-0.5 bg-black/50 border border-border rounded text-xs font-mono uppercase text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue"
          />
          <button
            type="submit"
            data-testid="add-ticker-button"
            aria-label="Add Ticker"
            className="p-1 rounded bg-accent-blue/20 border border-accent-blue/40 text-accent-blue hover:bg-accent-blue/30 text-xs flex items-center justify-center transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      {errorMsg && (
        <div className="px-3 py-1 bg-rose-950/80 border-b border-rose-800 text-[11px] font-mono text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Tickers List / Grid */}
      <div className="flex-1 overflow-y-auto divide-y divide-border/40 font-mono">
        {watchlist.map((item) => {
          const isSelected = item.ticker === selectedTicker;
          const changePct = item.change_pct ?? 0;
          const isUp = changePct >= 0;
          const flash = flashMap[item.ticker];

          let flashClass = '';
          if (flash === 'up') flashClass = 'animate-flash-green';
          else if (flash === 'down') flashClass = 'animate-flash-red';

          return (
            <div
              key={item.ticker}
              data-testid={`watchlist-item-${item.ticker}`}
              onClick={() => onSelectTicker(item.ticker)}
              className={`group px-3 py-2 flex items-center justify-between cursor-pointer transition-colors ${
                isSelected
                  ? 'bg-amber-500/10 border-l-2 border-accent-yellow'
                  : 'hover:bg-gray-800/40'
              } ${flashClass}`}
            >
              {/* Ticker & Name */}
              <div className="flex flex-col min-w-[70px]">
                <span className={`text-xs font-bold ${isSelected ? 'text-accent-yellow' : 'text-white'}`}>
                  {item.ticker}
                </span>
                {item.name && (
                  <span className="text-[10px] text-gray-500 truncate max-w-[80px]">
                    {item.name}
                  </span>
                )}
              </div>

              {/* Sparkline */}
              <div className="hidden sm:block">
                <Sparkline data={item.history || []} isUp={isUp} />
              </div>

              {/* Price & Change % */}
              <div className="flex items-center gap-2 text-right">
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-gray-100">
                    ${(item.price ?? 0).toFixed(2)}
                  </span>
                  <span className={`text-[10px] flex items-center justify-end gap-0.5 font-semibold ${isUp ? 'text-trade-up' : 'text-trade-down'}`}>
                    {isUp ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                    {isUp ? '+' : ''}{(item.change_pct ?? 0).toFixed(2)}%
                  </span>
                </div>

                {/* Remove Ticker Button */}
                <button
                  data-testid={`remove-ticker-${item.ticker}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveTicker(item.ticker);
                  }}
                  title={`Remove ${item.ticker}`}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-rose-400 transition-opacity"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
