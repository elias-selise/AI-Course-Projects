import React from 'react';
import { ConnectionStatus, Portfolio } from '../types';
import { Terminal, Activity, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';

interface HeaderProps {
  portfolio: Portfolio;
  connectionStatus: ConnectionStatus;
}

export const Header: React.FC<HeaderProps> = ({ portfolio, connectionStatus }) => {
  const total_value = portfolio?.total_value ?? 10000.0;
  const cash_balance = portfolio?.cash_balance ?? 10000.0;
  const unrealized_pnl = portfolio?.unrealized_pnl ?? 0;
  const unrealized_pnl_pct = portfolio?.unrealized_pnl_pct ?? 0;
  const isPositivePnl = unrealized_pnl >= 0;

  const getStatusBadge = () => {
    switch (connectionStatus) {
      case 'connected':
        return (
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-semibold tracking-wider">LIVE SSE</span>
          </div>
        );
      case 'reconnecting':
        return (
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-950/60 border border-amber-500/30 text-amber-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
            <span className="font-semibold tracking-wider">RECONNECTING</span>
          </div>
        );
      case 'disconnected':
        return (
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-rose-950/60 border border-rose-500/30 text-rose-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span className="font-semibold tracking-wider">DISCONNECTED</span>
          </div>
        );
    }
  };

  return (
    <header className="bg-panel border-b border-border px-4 py-2.5 flex flex-wrap items-center justify-between gap-4 select-none">
      {/* Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="p-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-accent-yellow flex items-center justify-center">
          <Terminal className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold font-mono tracking-wider text-accent-yellow">FINALLY</h1>
            <span className="text-xs px-1.5 py-0.2 rounded bg-accent-purple/20 border border-accent-purple/40 text-purple-300 font-mono">
              AI COPILOT
            </span>
          </div>
          <p className="text-[10px] text-gray-400 font-mono tracking-tight uppercase">Bloomberg AI Trading Workstation</p>
        </div>
      </div>

      {/* Center/Right Metrics & Status */}
      <div className="flex flex-wrap items-center gap-6">
        {/* Total Value */}
        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-mono text-gray-400 flex items-center gap-1">
            <Activity className="w-3 h-3 text-accent-blue" /> Total Portfolio Value
          </span>
          <span data-testid="portfolio-value" className="text-lg font-mono font-bold text-white tracking-tight">
            ${total_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>

        {/* Cash Balance */}
        <div className="flex flex-col border-l border-border pl-6">
          <span className="text-[10px] uppercase font-mono text-gray-400 flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-emerald-400" /> Cash Balance
          </span>
          <span data-testid="cash-balance" className="text-lg font-mono font-semibold text-gray-200">
            ${cash_balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>

        {/* Portfolio P&L */}
        <div className="flex flex-col border-l border-border pl-6">
          <span className="text-[10px] uppercase font-mono text-gray-400">Total Unrealized P&L</span>
          <div className={`flex items-center gap-1 font-mono font-bold text-base ${isPositivePnl ? 'text-trade-up' : 'text-trade-down'}`}>
            {isPositivePnl ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>{isPositivePnl ? '+' : ''}${unrealized_pnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            <span className="text-xs font-semibold px-1 rounded bg-black/40 border border-current opacity-90">
              ({isPositivePnl ? '+' : ''}{(unrealized_pnl_pct ?? 0).toFixed(2)}%)
            </span>
          </div>
        </div>

        {/* SSE Connection Indicator */}
        <div data-testid="connection-status" title="Live SSE Price Stream" className="border-l border-border pl-6 flex items-center">
          {getStatusBadge()}
        </div>
      </div>
    </header>
  );
};
