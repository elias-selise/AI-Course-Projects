import React, { useState } from 'react';
import { TickerData, Position } from '../types';
import { LineChart, BarChart2, TrendingUp, TrendingDown, Layers } from 'lucide-react';

interface MainChartAreaProps {
  tickerData?: TickerData;
  position?: Position;
}

export const MainChartArea: React.FC<MainChartAreaProps> = ({ tickerData, position }) => {
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | 'LIVE'>('LIVE');
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!tickerData) {
    return (
      <div className="bg-panel border border-border rounded p-6 flex flex-col items-center justify-center h-full text-gray-500 font-mono">
        <LineChart className="w-8 h-8 mb-2 opacity-50 text-accent-blue animate-pulse" />
        <p className="text-xs">SELECT A TICKER TO VIEW PRICE HISTORY</p>
      </div>
    );
  }

  const { ticker, name, price, change_pct, history = [] } = tickerData;
  const isUp = change_pct >= 0;

  // Build chart coordinates
  const prices = history.length > 0 ? history : [price * 0.98, price * 0.99, price, price * 1.01, price];
  const minPrice = Math.min(...prices) * 0.995;
  const maxPrice = Math.max(...prices) * 1.005;
  const priceRange = maxPrice - minPrice || 1;

  const svgWidth = 600;
  const svgHeight = 220;

  const points = prices.map((val, idx) => {
    const x = (idx / Math.max(1, prices.length - 1)) * svgWidth;
    const y = svgHeight - ((val - minPrice) / priceRange) * (svgHeight - 20) - 10;
    return { x, y, val };
  });

  const pathPoints = points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const areaPoints = `0,${svgHeight} ${pathPoints} ${svgWidth},${svgHeight}`;

  const hoveredPoint = hoverIndex !== null && points[hoverIndex] ? points[hoverIndex] : null;

  return (
    <div className="bg-panel border border-border rounded flex flex-col h-full overflow-hidden select-none">
      {/* Top Header */}
      <div className="bg-panel-header px-4 py-2.5 border-b border-border flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="p-1 rounded bg-accent-blue/10 border border-accent-blue/30 text-accent-blue">
            <BarChart2 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 font-mono">
              <h2 className="text-sm font-bold text-white tracking-wide">{ticker}</h2>
              <span className="text-xs text-gray-400 font-sans">{name || 'Asset Price'}</span>
            </div>
          </div>
        </div>

        {/* Live Price & Change Badge */}
        <div className="flex items-center gap-3 font-mono">
          <div className="text-right">
            <span className="text-lg font-bold text-white">${(price ?? 0).toFixed(2)}</span>
            <span className={`text-xs ml-2 font-semibold ${isUp ? 'text-trade-up' : 'text-trade-down'}`}>
              {isUp ? '+' : ''}{(change_pct ?? 0).toFixed(2)}%
            </span>
          </div>

          {/* Timeframe Controls */}
          <div className="flex items-center gap-1 bg-black/40 p-0.5 rounded border border-border">
            {(['1D', '1W', '1M', 'LIVE'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2 py-0.5 rounded text-[10px] font-mono transition-colors ${
                  timeframe === tf
                    ? 'bg-accent-blue text-white font-bold'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Position Summary Banner (if user holds position) */}
      {position && position.quantity > 0 && (
        <div className="bg-amber-950/20 border-b border-amber-500/20 px-4 py-1.5 flex items-center justify-between font-mono text-xs">
          <div className="flex items-center gap-2 text-accent-yellow">
            <Layers className="w-3.5 h-3.5" />
            <span className="font-semibold">POSITION: {position.quantity} shares @ ${(position.avg_cost ?? 0).toFixed(2)} avg</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-gray-400">Value: ${(position.market_value ?? 0).toFixed(2)}</span>
            <span className={`font-bold ${(position.unrealized_pnl ?? 0) >= 0 ? 'text-trade-up' : 'text-trade-down'}`}>
              P&L: {(position.unrealized_pnl ?? 0) >= 0 ? '+' : ''}${(position.unrealized_pnl ?? 0).toFixed(2)} ({(position.unrealized_pnl_pct ?? 0).toFixed(2)}%)
            </span>
          </div>
        </div>
      )}

      {/* SVG Chart Body */}
      <div className="flex-1 p-4 relative flex items-center justify-center min-h-[220px]">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-full overflow-visible"
          onMouseLeave={() => setHoverIndex(null)}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const ratio = mouseX / rect.width;
            const idx = Math.min(
              points.length - 1,
              Math.max(0, Math.round(ratio * (points.length - 1)))
            );
            setHoverIndex(idx);
          }}
        >
          <defs>
            <linearGradient id={`gradient-${ticker}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isUp ? '#22c55e' : '#ef4444'} stopOpacity="0.25" />
              <stop offset="100%" stopColor={isUp ? '#22c55e' : '#ef4444'} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1="0" y1="40" x2={svgWidth} y2="40" stroke="#30363d" strokeDasharray="3 3" opacity="0.5" />
          <line x1="0" y1="110" x2={svgWidth} y2="110" stroke="#30363d" strokeDasharray="3 3" opacity="0.5" />
          <line x1="0" y1="180" x2={svgWidth} y2="180" stroke="#30363d" strokeDasharray="3 3" opacity="0.5" />

          {/* Area Fill */}
          <polygon points={areaPoints} fill={`url(#gradient-${ticker})`} />

          {/* Main Price Line */}
          <polyline
            fill="none"
            stroke={isUp ? '#22c55e' : '#ef4444'}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={pathPoints}
          />

          {/* Hover Pointer Line and Tooltip */}
          {hoveredPoint && (
            <g>
              <line
                x1={hoveredPoint.x}
                y1={0}
                x2={hoveredPoint.x}
                y2={svgHeight}
                stroke="#ecad0a"
                strokeDasharray="2 2"
                strokeWidth="1"
              />
              <circle
                cx={hoveredPoint.x}
                cy={hoveredPoint.y}
                r="4"
                fill="#ecad0a"
                stroke="#0d1117"
                strokeWidth="2"
              />
            </g>
          )}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredPoint && (
          <div
            className="absolute bg-panel border border-accent-yellow px-2 py-1 rounded text-xs font-mono shadow-lg pointer-events-none z-10 text-white"
            style={{
              left: `${(hoveredPoint.x / svgWidth) * 90}%`,
              top: '12px',
            }}
          >
            <div className="text-gray-400 text-[10px]">PRICE POINT</div>
            <div className="text-accent-yellow font-bold">${hoveredPoint.val.toFixed(2)}</div>
          </div>
        )}
      </div>

      {/* Chart Footer Stats */}
      <div className="bg-panel-header px-4 py-2 border-t border-border flex items-center justify-between text-[11px] font-mono text-gray-400">
        <span>MIN: ${minPrice.toFixed(2)}</span>
        <span>RANGE: ${(maxPrice - minPrice).toFixed(2)}</span>
        <span>MAX: ${maxPrice.toFixed(2)}</span>
      </div>
    </div>
  );
};
