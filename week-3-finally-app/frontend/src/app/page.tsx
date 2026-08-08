'use client';

import React, { useEffect } from 'react';
import { useMarketStream } from '@/hooks/useMarketStream';
import { useTerminalStore } from '@/store/useTerminalStore';
import { TerminalHeader } from '@/components/Header';
import { WatchlistGrid } from '@/components/WatchlistGrid';
import { TradeBar } from '@/components/TradeBar';
import { MainPriceChart } from '@/components/MainPriceChart';
import { PortfolioHeatmap } from '@/components/PortfolioHeatmap';
import { PositionsTable } from '@/components/PositionsTable';
import { PortfolioPnLChart } from '@/components/PortfolioPnLChart';
import { AIChatPanel } from '@/components/AIChatPanel';

export default function WorkstationPage() {
  const { status, prices, sparklines, flashes } = useMarketStream('/api/stream/prices');
  const { portfolio, fetchPortfolio, fetchWatchlist, fetchHistory, fetchChatHistory } =
    useTerminalStore();

  useEffect(() => {
    fetchPortfolio();
    fetchWatchlist();
    fetchHistory();
    fetchChatHistory();
  }, [fetchPortfolio, fetchWatchlist, fetchHistory, fetchChatHistory]);

  return (
    <div className="min-h-screen bg-terminal-bg text-gray-100 flex flex-col font-mono selection:bg-terminal-blue selection:text-white">
      {/* Workstation Header */}
      <TerminalHeader status={status} portfolio={portfolio} />

      {/* Main Terminal Workstation Layout */}
      <div className="flex-1 p-3 flex flex-col lg:flex-row gap-3 overflow-hidden">
        {/* Main Workspace (Left & Center Columns) */}
        <div className="flex-1 flex flex-col gap-3 min-w-0">
          {/* Row 1: Watchlist & Order Entry Trade Bar */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-3">
            <div className="xl:col-span-2">
              <WatchlistGrid prices={prices} sparklines={sparklines} flashes={flashes} />
            </div>
            <div className="xl:col-span-1">
              <TradeBar />
            </div>
          </div>

          {/* Row 2: Interactive Price Chart & Portfolio Heatmap */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 flex-1 min-h-[260px]">
            <MainPriceChart prices={prices} sparklines={sparklines} />
            <PortfolioHeatmap />
          </div>

          {/* Row 3: Active Positions Table & Valuation P&L Timeline */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 flex-1 min-h-[260px]">
            <PositionsTable />
            <PortfolioPnLChart />
          </div>
        </div>

        {/* Right Sidebar Column: FinAlly AI Copilot Panel */}
        <div className="w-full lg:w-80 xl:w-96 flex-shrink-0 h-[600px] lg:h-auto">
          <AIChatPanel />
        </div>
      </div>
    </div>
  );
}
