import React from 'react';
import { Position } from '../types';
import { Briefcase, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface PositionsTableProps {
  positions: Position[];
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
  onQuickTrade?: (ticker: string, side: 'buy' | 'sell') => void;
}

export const PositionsTable: React.FC<PositionsTableProps> = ({
  positions,
  selectedTicker,
  onSelectTicker,
  onQuickTrade,
}) => {
  const activePositions = positions.filter(p => p.quantity > 0);

  return (
    <div data-testid="positions-table" className="bg-panel border border-border rounded flex flex-col h-full overflow-hidden select-none">
      {/* Header */}
      <div className="bg-panel-header px-3.5 py-2.5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-accent-yellow" />
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-accent-yellow">
            OPEN POSITIONS ({activePositions.length})
          </h2>
        </div>
      </div>

      {/* Table Body */}
      <div className="flex-1 overflow-x-auto overflow-y-auto">
        {activePositions.length === 0 ? (
          <div className="p-8 text-center text-gray-500 font-mono text-xs">
            NO OPEN POSITIONS HELD
          </div>
        ) : (
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="bg-black/30 border-b border-border text-[10px] text-gray-400 uppercase tracking-wider">
                <th className="px-3 py-2">Ticker</th>
                <th className="px-3 py-2 text-right">Qty</th>
                <th className="px-3 py-2 text-right">Avg Cost</th>
                <th className="px-3 py-2 text-right">Price</th>
                <th className="px-3 py-2 text-right">Market Value</th>
                <th className="px-3 py-2 text-right">Unrealized P&L</th>
                <th className="px-3 py-2 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {activePositions.map((pos) => {
                const isSelected = pos.ticker === selectedTicker;
                const isPos = pos.unrealized_pnl >= 0;

                return (
                  <tr
                    key={pos.ticker}
                    data-testid={`position-row-${pos.ticker}`}
                    onClick={() => onSelectTicker(pos.ticker)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-amber-500/10 text-white font-bold'
                        : 'hover:bg-gray-800/40 text-gray-200'
                    }`}
                  >
                    <td className="px-3 py-2.5 text-right font-bold text-accent-yellow flex items-center gap-1">
                      {pos.ticker}
                    </td>
                    <td className="px-3 py-2.5 text-right">{pos.quantity ?? 0}</td>
                    <td className="px-3 py-2.5 text-right text-gray-400">${(pos.avg_cost ?? 0).toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-right text-white font-semibold">${(pos.current_price ?? 0).toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-right text-white font-bold">
                      ${(pos.market_value ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className={`px-3 py-2.5 text-right font-bold ${isPos ? 'text-trade-up' : 'text-trade-down'}`}>
                      <div className="flex items-center justify-end gap-1">
                        {isPos ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                        <span>{isPos ? '+' : ''}${(pos.unrealized_pnl ?? 0).toFixed(2)}</span>
                        <span className="text-[10px] text-gray-400">({isPos ? '+' : ''}{(pos.unrealized_pnl_pct ?? 0).toFixed(2)}%)</span>
                      </div>
                    </td>
                    <td className="px-3 py-2.5 text-center" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => onQuickTrade && onQuickTrade(pos.ticker, 'buy')}
                          className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-600 text-emerald-400 hover:bg-emerald-800 text-[10px] transition-colors"
                        >
                          BUY
                        </button>
                        <button
                          onClick={() => onQuickTrade && onQuickTrade(pos.ticker, 'sell')}
                          className="px-2 py-0.5 rounded bg-rose-950 border border-rose-600 text-rose-400 hover:bg-rose-800 text-[10px] transition-colors"
                        >
                          SELL
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
