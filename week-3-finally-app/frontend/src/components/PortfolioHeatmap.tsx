import React from 'react';
import { Position } from '../types';
import { LayoutGrid, PieChart } from 'lucide-react';

interface PortfolioHeatmapProps {
  positions: Position[];
  onSelectTicker?: (ticker: string) => void;
}

export const PortfolioHeatmap: React.FC<PortfolioHeatmapProps> = ({ positions, onSelectTicker }) => {
  const activePositions = positions.filter(p => p.quantity > 0);
  const totalMarketValue = activePositions.reduce((sum, p) => sum + (p.quantity * p.current_price), 0);

  const getPnlBgColor = (pnlPct: number) => {
    if (pnlPct >= 10) return 'bg-emerald-600 border-emerald-400 text-white';
    if (pnlPct > 0) return 'bg-emerald-800/80 border-emerald-600 text-emerald-100';
    if (pnlPct === 0) return 'bg-gray-800 border-gray-600 text-gray-200';
    if (pnlPct > -10) return 'bg-rose-900/80 border-rose-700 text-rose-100';
    return 'bg-rose-700 border-rose-500 text-white';
  };

  return (
    <div data-testid="portfolio-heatmap" className="bg-panel border border-border rounded flex flex-col h-full overflow-hidden select-none">
      {/* Header */}
      <div className="bg-panel-header px-3.5 py-2.5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LayoutGrid className="w-4 h-4 text-accent-yellow" />
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-accent-yellow">
            PORTFOLIO HEATMAP (TREEMAP)
          </h2>
        </div>
        <span className="text-[10px] font-mono text-gray-400">
          WEIGHTED BY POSITION VALUE
        </span>
      </div>

      {/* Heatmap Area */}
      <div className="flex-1 p-3 min-h-[160px] overflow-hidden">
        {activePositions.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 font-mono text-xs p-4 text-center border border-dashed border-border rounded">
            <PieChart className="w-8 h-8 mb-2 opacity-40 text-accent-blue" />
            <p className="font-semibold text-gray-400">NO ACTIVE POSITIONS</p>
            <p className="text-[11px] text-gray-500 mt-1">
              Use the Trade Bar or AI Copilot to execute buy orders.
            </p>
          </div>
        ) : (
          <div className="h-full flex flex-wrap gap-1.5 align-stretch">
            {activePositions.map((pos) => {
              const marketVal = pos.quantity * pos.current_price;
              const weight = totalMarketValue > 0 ? (marketVal / totalMarketValue) : (1 / activePositions.length);
              const flexGrow = Math.max(1, Math.round(weight * 100));
              const pnlIsPos = pos.unrealized_pnl >= 0;

              return (
                <div
                  key={pos.ticker}
                  onClick={() => onSelectTicker && onSelectTicker(pos.ticker)}
                  style={{ flex: `${flexGrow} 1 120px` }}
                  className={`group relative p-2.5 rounded border transition-all duration-200 cursor-pointer flex flex-col justify-between overflow-hidden shadow-sm hover:scale-[1.01] ${getPnlBgColor(
                    pos.unrealized_pnl_pct
                  )}`}
                >
                  <div className="flex items-center justify-between font-mono">
                    <span className="font-bold text-sm tracking-wider uppercase drop-shadow-sm">
                      {pos.ticker}
                    </span>
                    <span className="text-[10px] font-semibold opacity-90">
                      {(weight * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="mt-2 font-mono">
                    <div className="text-xs font-bold">
                      ${marketVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                    <div className="text-[11px] font-semibold mt-0.5">
                      {pnlIsPos ? '+' : ''}${(pos.unrealized_pnl ?? 0).toFixed(2)} ({pnlIsPos ? '+' : ''}{(pos.unrealized_pnl_pct ?? 0).toFixed(2)}%)
                    </div>
                  </div>

                  {/* Tooltip Overlay */}
                  <div className="absolute inset-0 bg-black/90 p-2 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-center text-[10px] font-mono text-white pointer-events-none">
                    <div className="font-bold text-accent-yellow mb-1">{pos.ticker} Position</div>
                    <div>Qty: {pos.quantity} shares</div>
                    <div>Avg Cost: ${(pos.avg_cost ?? 0).toFixed(2)}</div>
                    <div>Price: ${(pos.current_price ?? 0).toFixed(2)}</div>
                    <div>Market Val: ${marketVal.toFixed(2)}</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
