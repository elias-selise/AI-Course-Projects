'use client';

import React, { useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { Position } from '@/types';

export const PositionsTable: React.FC = () => {
  const { portfolio, executeTrade, setSelectedTicker, selectedTicker } =
    useTerminalStore();

  const [sellingTicker, setSellingTicker] = useState<string | null>(null);

  const positions: Position[] = portfolio?.positions || [];

  const handleSellAll = async (pos: Position) => {
    setSellingTicker(pos.ticker);
    try {
      await executeTrade(pos.ticker, 'sell', pos.quantity);
    } catch (err) {
      console.error('Sell execution failed:', err);
    } finally {
      setSellingTicker(null);
    }
  };

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col h-full overflow-hidden">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-terminal-yellow mb-2">
        Active Portfolio Positions ({positions.length})
      </h2>

      <div className="overflow-x-auto overflow-y-auto max-h-[220px] flex-1">
        <table className="w-full text-left text-xs font-mono border-collapse">
          <thead>
            <tr className="border-b border-terminal-border text-terminal-muted uppercase text-[10px] sticky top-0 bg-terminal-card z-10">
              <th className="py-1.5 px-2">Ticker</th>
              <th className="py-1.5 px-2 text-right">Qty</th>
              <th className="py-1.5 px-2 text-right">Avg Cost</th>
              <th className="py-1.5 px-2 text-right">Current</th>
              <th className="py-1.5 px-2 text-right">Market Val</th>
              <th className="py-1.5 px-2 text-right">Unrealized P&L</th>
              <th className="py-1.5 px-2 text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {positions.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-6 text-center text-terminal-muted italic">
                  No active open positions in portfolio.
                </td>
              </tr>
            ) : (
              positions.map((pos) => {
                const isProfitable = pos.unrealized_pnl >= 0;
                const isSelected = selectedTicker === pos.ticker;

                return (
                  <tr
                    key={pos.ticker}
                    onClick={() => setSelectedTicker(pos.ticker)}
                    className={`border-b border-terminal-border/50 hover:bg-terminal-bg/60 cursor-pointer transition ${
                      isSelected ? 'bg-terminal-bg/80' : ''
                    }`}
                  >
                    <td className="py-2 px-2 font-bold text-white flex items-center space-x-1">
                      <span>{pos.ticker}</span>
                    </td>
                    <td className="py-2 px-2 text-right text-gray-200">{pos.quantity}</td>
                    <td className="py-2 px-2 text-right text-gray-300">
                      ${pos.avg_cost.toFixed(2)}
                    </td>
                    <td className="py-2 px-2 text-right text-white font-semibold">
                      ${pos.current_price.toFixed(2)}
                    </td>
                    <td className="py-2 px-2 text-right text-white font-semibold">
                      ${pos.market_value.toFixed(2)}
                    </td>
                    <td
                      className={`py-2 px-2 text-right font-semibold ${
                        isProfitable ? 'text-emerald-400' : 'text-red-400'
                      }`}
                    >
                      {isProfitable ? '+' : ''}${pos.unrealized_pnl.toFixed(2)} (
                      {isProfitable ? '+' : ''}
                      {pos.unrealized_pnl_percent.toFixed(2)}%)
                    </td>
                    <td className="py-2 px-2 text-center" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleSellAll(pos)}
                        disabled={sellingTicker === pos.ticker}
                        className="px-2 py-0.5 bg-red-600/20 hover:bg-red-600/40 border border-red-500/50 text-red-400 hover:text-red-300 rounded text-[10px] uppercase font-bold transition disabled:opacity-50"
                      >
                        {sellingTicker === pos.ticker ? 'SELLING...' : 'SELL ALL'}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
