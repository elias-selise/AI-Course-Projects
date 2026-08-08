'use client';

import React, { useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { PriceTick } from '@/types';
import { TrendingUp, TrendingDown, Plus, Trash2 } from 'lucide-react';

interface WatchlistGridProps {
  prices: Record<string, PriceTick>;
  sparklines: Record<string, number[]>;
  flashes: Record<string, 'up' | 'down' | null>;
}

// Mini SVG Sparkline Component
const Sparkline: React.FC<{ data?: number[]; isPositive: boolean }> = ({
  data = [],
  isPositive,
}) => {
  if (!data || data.length < 2) {
    return (
      <svg className="w-20 h-6 overflow-visible" viewBox="0 0 80 24">
        <line x1="0" y1="12" x2="80" y2="12" stroke="#4b5563" strokeWidth="1.5" />
      </svg>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min === 0 ? 1 : max - min;

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * 80;
      const y = 22 - ((val - min) / range) * 20;
      return `${x},${y}`;
    })
    .join(' ');

  const strokeColor = isPositive ? '#22c55e' : '#ef4444';

  return (
    <svg className="w-20 h-6 overflow-visible" viewBox="0 0 80 24">
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

export const WatchlistGrid: React.FC<WatchlistGridProps> = ({
  prices,
  sparklines,
  flashes,
}) => {
  const {
    watchlist,
    selectedTicker,
    setSelectedTicker,
    addWatchlistTicker,
    removeWatchlistTicker,
  } = useTerminalStore();

  const [newTickerInput, setNewTickerInput] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddTicker = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTickerInput.trim()) return;
    setIsAdding(true);
    try {
      await addWatchlistTicker(newTickerInput.trim().toUpperCase());
      setNewTickerInput('');
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-terminal-yellow">
          Watchlist & Live Tickers
        </h2>
        <form onSubmit={handleAddTicker} className="flex items-center space-x-1">
          <input
            type="text"
            placeholder="ADD TICKER"
            value={newTickerInput}
            onChange={(e) => setNewTickerInput(e.target.value)}
            className="w-20 px-2 py-0.5 text-xs bg-terminal-bg border border-terminal-border rounded text-white focus:outline-none focus:border-terminal-blue uppercase"
          />
          <button
            type="submit"
            disabled={isAdding}
            className="p-1 bg-terminal-blue/20 hover:bg-terminal-blue/40 text-terminal-blue rounded border border-terminal-blue/50 text-xs transition"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 overflow-y-auto max-h-[160px] pr-1">
        {watchlist.map((item) => {
          const tick = prices[item.ticker];
          const currentPrice = tick ? tick.price : item.price;
          const change = tick ? tick.change : item.change;
          const isPositive = change >= 0;
          const isSelected = selectedTicker === item.ticker;
          const flash = flashes[item.ticker];

          let flashClass = '';
          if (flash === 'up') flashClass = 'animate-flash-green border-emerald-500/80';
          if (flash === 'down') flashClass = 'animate-flash-red border-red-500/80';

          return (
            <div
              key={item.ticker}
              onClick={() => setSelectedTicker(item.ticker)}
              className={`p-2 rounded border cursor-pointer transition flex flex-col justify-between ${
                isSelected
                  ? 'border-terminal-yellow bg-terminal-bg/80 shadow-[0_0_8px_rgba(236,173,10,0.2)]'
                  : 'border-terminal-border bg-terminal-bg/40 hover:bg-terminal-bg/80'
              } ${flashClass}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-white tracking-wide">
                  {item.ticker}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeWatchlistTicker(item.ticker);
                  }}
                  className="text-terminal-muted hover:text-red-400 p-0.5 rounded"
                  title="Remove Ticker"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>

              <div className="my-1 flex items-baseline justify-between">
                <span className="font-mono text-xs font-semibold text-white">
                  ${currentPrice.toFixed(2)}
                </span>
                <div
                  className={`flex items-center text-[10px] font-mono ${
                    isPositive ? 'text-emerald-400' : 'text-red-400'
                  }`}
                >
                  {isPositive ? (
                    <TrendingUp className="w-3 h-3 mr-0.5 inline" />
                  ) : (
                    <TrendingDown className="w-3 h-3 mr-0.5 inline" />
                  )}
                  {isPositive ? '+' : ''}
                  {change.toFixed(2)}%
                </div>
              </div>

              <div className="mt-1 flex justify-center">
                <Sparkline
                  data={sparklines[item.ticker]}
                  isPositive={isPositive}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
