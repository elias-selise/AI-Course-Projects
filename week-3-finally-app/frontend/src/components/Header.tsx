'use client';

import React from 'react';
import { StreamStatus, Portfolio } from '@/types';
import { Activity, DollarSign, Wallet } from 'lucide-react';

interface HeaderProps {
  status: StreamStatus;
  portfolio: Portfolio | null;
}

export const TerminalHeader: React.FC<HeaderProps> = ({ status, portfolio }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]';
      case 'reconnecting':
        return 'bg-yellow-500 animate-pulse';
      case 'disconnected':
        return 'bg-red-500';
    }
  };

  return (
    <header className="h-14 border-b border-terminal-border bg-terminal-card/80 backdrop-blur px-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Activity className="w-5 h-5 text-terminal-yellow" />
        <span className="font-bold tracking-wider text-white text-lg">FinAlly</span>
        <span className="text-xs px-2 py-0.5 rounded bg-terminal-purple/30 text-purple-300 font-mono">
          TERMINAL v1.0
        </span>
      </div>

      <div className="flex items-center space-x-6">
        {/* Total Value */}
        <div className="flex items-center space-x-2">
          <DollarSign className="w-4 h-4 text-terminal-blue" />
          <span className="text-xs text-terminal-muted uppercase">Portfolio Value:</span>
          <span className="font-mono text-sm font-semibold text-white">
            $
            {portfolio
              ? portfolio.total_value.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })
              : '10,000.00'}
          </span>
        </div>

        {/* Cash Balance */}
        <div className="flex items-center space-x-2">
          <Wallet className="w-4 h-4 text-terminal-yellow" />
          <span className="text-xs text-terminal-muted uppercase">Cash:</span>
          <span className="font-mono text-sm font-semibold text-white">
            $
            {portfolio
              ? portfolio.cash_balance.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })
              : '10,000.00'}
          </span>
        </div>

        {/* Connection Status Dot */}
        <div className="flex items-center space-x-2 bg-terminal-bg/50 px-2.5 py-1 rounded border border-terminal-border">
          <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor()}`} />
          <span className="text-xs font-mono uppercase text-terminal-muted">{status}</span>
        </div>
      </div>
    </header>
  );
};
