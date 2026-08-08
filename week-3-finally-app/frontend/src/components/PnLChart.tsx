import React from 'react';
import { PortfolioSnapshot } from '../types';
import { TrendingUp, DollarSign } from 'lucide-react';

interface PnLChartProps {
  history: PortfolioSnapshot[];
  currentValue: number;
}

export const PnLChart: React.FC<PnLChartProps> = ({ history, currentValue }) => {
  const initialValue = 10000.0;
  const values = history.length > 0 ? history.map(h => h.total_value) : [10000.0, currentValue];
  
  const minVal = Math.min(...values, initialValue * 0.95);
  const maxVal = Math.max(...values, initialValue * 1.05);
  const range = maxVal - minVal || 1;

  const svgWidth = 500;
  const svgHeight = 160;

  const points = values.map((val, idx) => {
    const x = (idx / Math.max(1, values.length - 1)) * svgWidth;
    const y = svgHeight - ((val - minVal) / range) * (svgHeight - 20) - 10;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  const baselineY = svgHeight - ((initialValue - minVal) / range) * (svgHeight - 20) - 10;
  const areaPoints = `0,${svgHeight} ${points} ${svgWidth},${svgHeight}`;

  const isNetProfit = currentValue >= initialValue;
  const returnAmt = currentValue - initialValue;
  const returnPct = (returnAmt / initialValue) * 100;

  return (
    <div data-testid="pnl-chart" className="bg-panel border border-border rounded flex flex-col h-full overflow-hidden select-none">
      {/* Header */}
      <div className="bg-panel-header px-3.5 py-2.5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-accent-blue" />
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-accent-blue">
            PORTFOLIO EQUITY CURVE (P&L HISTORY)
          </h2>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-gray-400">Total Return:</span>
          <span className={`font-bold ${isNetProfit ? 'text-trade-up' : 'text-trade-down'}`}>
            {isNetProfit ? '+' : ''}${returnAmt.toFixed(2)} ({isNetProfit ? '+' : ''}{returnPct.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* SVG Chart */}
      <div className="flex-1 p-3 relative flex items-center justify-center min-h-[160px]">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-full overflow-visible">
          <defs>
            <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isNetProfit ? '#209dd7' : '#ef4444'} stopOpacity="0.3" />
              <stop offset="100%" stopColor={isNetProfit ? '#209dd7' : '#ef4444'} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Baseline ($10,000 start) */}
          <line
            x1="0"
            y1={baselineY}
            x2={svgWidth}
            y2={baselineY}
            stroke="#ecad0a"
            strokeDasharray="4 4"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Area under curve */}
          <polygon points={areaPoints} fill="url(#pnlGradient)" />

          {/* Value Line */}
          <polyline
            fill="none"
            stroke={isNetProfit ? '#209dd7' : '#ef4444'}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
          />
        </svg>
      </div>

      {/* Footer Legend */}
      <div className="bg-panel-header px-3.5 py-1.5 border-t border-border flex items-center justify-between text-[10px] font-mono text-gray-400">
        <span className="flex items-center gap-1">
          <span className="w-2 h-0.5 bg-accent-yellow inline-block" /> Baseline: $10,000.00
        </span>
        <span>PEAK: ${maxVal.toFixed(2)}</span>
        <span>LOW: ${minVal.toFixed(2)}</span>
      </div>
    </div>
  );
};
