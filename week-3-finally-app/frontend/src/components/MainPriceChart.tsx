'use client';

import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import { useTerminalStore } from '@/store/useTerminalStore';
import { PriceTick } from '@/types';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MainPriceChartProps {
  prices: Record<string, PriceTick>;
  sparklines: Record<string, number[]>;
}

export const MainPriceChart: React.FC<MainPriceChartProps> = ({
  prices,
  sparklines,
}) => {
  const { selectedTicker } = useTerminalStore();
  const [timeframe, setTimeframe] = useState<'1M' | '5M' | '15M' | 'LIVE'>('LIVE');

  const currentTick = prices[selectedTicker];
  const history = sparklines[selectedTicker] || [];

  // Filter or slice history according to timeframe selection
  let sliceCount = 30;
  if (timeframe === '1M') sliceCount = 10;
  if (timeframe === '5M') sliceCount = 20;
  if (timeframe === '15M') sliceCount = 30;

  const displayPrices = history.slice(-sliceCount);

  // Format data points for Recharts
  const chartData = displayPrices.map((price, idx) => ({
    time: `T-${displayPrices.length - idx}`,
    price: price,
  }));

  const latestPrice = currentTick ? currentTick.price : (displayPrices[displayPrices.length - 1] || 100);
  const change = currentTick ? currentTick.change : 0.0;
  const isPositive = change >= 0;

  const minPrice = displayPrices.length ? Math.floor(Math.min(...displayPrices) * 0.99) : 90;
  const maxPrice = displayPrices.length ? Math.ceil(Math.max(...displayPrices) * 1.01) : 110;

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-bold text-white tracking-wider font-mono">
            {selectedTicker} / USD
          </span>
          <span className="text-base font-bold font-mono text-terminal-yellow">
            ${latestPrice.toFixed(2)}
          </span>
          <div
            className={`flex items-center px-1.5 py-0.5 rounded text-xs font-mono font-semibold ${
              isPositive
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'bg-red-500/20 text-red-400 border border-red-500/40'
            }`}
          >
            {isPositive ? (
              <TrendingUp className="w-3 h-3 mr-1 inline" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1 inline" />
            )}
            {isPositive ? '+' : ''}
            {change.toFixed(2)}%
          </div>
        </div>

        {/* Timeframe Buttons */}
        <div className="flex items-center space-x-1">
          {(['1M', '5M', '15M', 'LIVE'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2 py-0.5 text-xs font-mono rounded transition ${
                timeframe === tf
                  ? 'bg-terminal-blue text-white font-bold'
                  : 'bg-terminal-bg text-terminal-muted hover:text-white border border-terminal-border'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Area */}
      <div className="w-full h-[220px] min-h-[220px] relative">
        {chartData.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-terminal-muted text-xs font-mono">
            Buffering market data ticks...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#209dd7" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#209dd7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#4b5563" tick={{ fontSize: 10 }} />
              <YAxis
                domain={[minPrice, maxPrice]}
                stroke="#4b5563"
                tick={{ fontSize: 10 }}
                tickFormatter={(val) => `$${val}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  borderColor: '#21262d',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
                formatter={(val: number) => [`$${val.toFixed(2)}`, 'Price']}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#209dd7"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#priceGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
