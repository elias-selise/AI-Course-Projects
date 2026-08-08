'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from '../components/Header';
import { WatchlistPanel } from '../components/WatchlistPanel';
import { MainChartArea } from '../components/MainChartArea';
import { PortfolioHeatmap } from '../components/PortfolioHeatmap';
import { PnLChart } from '../components/PnLChart';
import { PositionsTable } from '../components/PositionsTable';
import { TradeBar } from '../components/TradeBar';
import { AIChatSidebar } from '../components/AIChatSidebar';
import { useSSE, PriceUpdatePayload } from '../hooks/useSSE';
import {
  fetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  fetchPortfolio,
  executeTrade,
  fetchPortfolioHistory,
  sendChatMessage,
} from '../services/api';
import {
  Portfolio,
  PortfolioSnapshot,
  TickerData,
  ChatMessage,
  Side,
} from '../types';

export default function Home() {
  const [watchlist, setWatchlist] = useState<TickerData[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio>({
    cash_balance: 10000.0,
    total_value: 10000.0,
    unrealized_pnl: 0,
    unrealized_pnl_pct: 0,
    positions: [],
  });
  const [portfolioHistory, setPortfolioHistory] = useState<PortfolioSnapshot[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>('AAPL');
  const [flashMap, setFlashMap] = useState<Record<string, 'up' | 'down'>>({});
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      role: 'assistant',
      content: "Welcome to FinAlly AI Trading Workstation! I am your AI Copilot. You can monitor streaming market prices, manage your portfolio, or ask me to analyze risks or execute trades for you.",
      timestamp: '2026-01-01T00:00:00.000Z',
    },
  ]);
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);

  // Initial Data Fetch
  const loadInitialData = useCallback(async () => {
    try {
      const wl = await fetchWatchlist();
      if (wl && wl.length > 0) {
        setWatchlist(wl);
        if (!selectedTicker) {
          setSelectedTicker(wl[0].ticker);
        }
      }
    } catch (err) {
      console.error('Error loading watchlist:', err);
    }

    try {
      const port = await fetchPortfolio();
      if (port) {
        setPortfolio(port);
      }
    } catch (err) {
      console.error('Error loading portfolio:', err);
    }

    try {
      const hist = await fetchPortfolioHistory();
      if (hist) {
        setPortfolioHistory(hist);
      }
    } catch (err) {
      console.error('Error loading portfolio history:', err);
    }
  }, [selectedTicker]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle live price updates from SSE stream
  const handlePriceUpdate = useCallback(
    (updates: PriceUpdatePayload | PriceUpdatePayload[]) => {
      const updateList = Array.isArray(updates) ? updates : [updates];

      setWatchlist((prevWatchlist) => {
        if (prevWatchlist.length === 0) return prevWatchlist;

        const newFlash: Record<string, 'up' | 'down'> = {};
        const updatedWatchlist = prevWatchlist.map((item) => {
          const match = updateList.find((u) => u.ticker === item.ticker);
          if (!match) return item;

          let newPrice = match.price;
          if (newPrice <= 0) {
            // Apply delta if mock SSE doesn't specify absolute price
            const changePct = match.change_pct || 0;
            const currentItemPrice = item.price ?? 100.0;
            newPrice = Number((currentItemPrice * (1 + changePct / 100)).toFixed(2));
          }

          const direction = newPrice >= (item.price ?? 0) ? 'up' : 'down';
          if (newPrice !== item.price) {
            newFlash[item.ticker] = direction;
          }

          const prevP = item.prev_price ?? newPrice;
          const changePct =
            match.change_pct !== undefined
              ? match.change_pct
              : prevP > 0
              ? Number((((newPrice - prevP) / prevP) * 100).toFixed(2))
              : (item.change_pct ?? 0);

          const updatedHistory = [...(item.history || []), newPrice].slice(-30);

          return {
            ...item,
            price: newPrice,
            prev_price: item.price,
            change_pct: changePct,
            history: updatedHistory,
          };
        });

        // Trigger brief CSS flash animation
        if (Object.keys(newFlash).length > 0) {
          setFlashMap((prev) => ({ ...prev, ...newFlash }));
          setTimeout(() => {
            setFlashMap((prev) => {
              const next = { ...prev };
              Object.keys(newFlash).forEach((t) => delete next[t]);
              return next;
            });
          }, 600);
        }

        return updatedWatchlist;
      });

      // Update active portfolio open position prices & total value in real time
      setPortfolio((prevPort) => {
        if (!prevPort.positions || prevPort.positions.length === 0) return prevPort;

        let positionsChanged = false;
        const updatedPositions = prevPort.positions.map((pos) => {
          const match = updateList.find((u) => u.ticker === pos.ticker);
          if (!match) return pos;

          const newPrice = match.price > 0 ? match.price : pos.current_price;

          positionsChanged = true;
          const marketValue = pos.quantity * newPrice;
          const unrealizedPnl = (newPrice - pos.avg_cost) * pos.quantity;
          const unrealizedPnlPct = pos.avg_cost > 0 ? ((newPrice - pos.avg_cost) / pos.avg_cost) * 100 : 0;

          return {
            ...pos,
            current_price: newPrice,
            market_value: marketValue,
            unrealized_pnl: unrealizedPnl,
            unrealized_pnl_pct: unrealizedPnlPct,
          };
        });

        if (!positionsChanged) return prevPort;

        const posValue = updatedPositions.reduce((sum, p) => sum + p.market_value, 0);
        const posCost = updatedPositions.reduce((sum, p) => sum + p.quantity * p.avg_cost, 0);
        const totalVal = prevPort.cash_balance + posValue;
        const totalPnl = posValue - posCost;
        const totalPnlPct = posCost > 0 ? (totalPnl / posCost) * 100 : 0;

        return {
          ...prevPort,
          total_value: totalVal,
          unrealized_pnl: totalPnl,
          unrealized_pnl_pct: totalPnlPct,
          positions: updatedPositions,
        };
      });
    },
    []
  );

  const { status: connectionStatus } = useSSE(handlePriceUpdate);

  // Watchlist handlers
  const handleAddTicker = useCallback(async (ticker: string) => {
    const res = await addToWatchlist(ticker);
    if (res.success) {
      const updatedWl = await fetchWatchlist();
      setWatchlist(updatedWl);
      setSelectedTicker(ticker);
    }
  }, []);

  const handleRemoveTicker = useCallback(async (ticker: string) => {
    const res = await removeFromWatchlist(ticker);
    if (res.success) {
      const updatedWl = await fetchWatchlist();
      setWatchlist(updatedWl);
      if (updatedWl.length > 0) {
        setSelectedTicker(updatedWl[0].ticker);
      }
    }
  }, []);

  // Trade execution handler
  const handleExecuteTrade = useCallback(async (ticker: string, quantity: number, side: Side) => {
    const res = await executeTrade(ticker, quantity, side);
    if (res.success) {
      try {
        const [updatedPort, updatedHist] = await Promise.all([
          fetchPortfolio(),
          fetchPortfolioHistory(),
        ]);
        setPortfolio(updatedPort);
        setPortfolioHistory(updatedHist);
      } catch (e) {
        console.error(e);
      }
      return { success: true, message: res.message };
    }
    return { success: false, message: res.message };
  }, []);

  // AI Chat handler
  const handleSendMessage = useCallback(async (content: string) => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);

    const chatRes = await sendChatMessage(content);

    // Auto-execute trades requested by AI
    if (chatRes.trades && chatRes.trades.length > 0) {
      for (const trade of chatRes.trades) {
        await executeTrade(trade.ticker, trade.quantity, trade.side);
      }
    }

    // Process watchlist changes requested by AI
    if (chatRes.watchlist_changes && chatRes.watchlist_changes.length > 0) {
      for (const change of chatRes.watchlist_changes) {
        if (change.action === 'add') {
          await addToWatchlist(change.ticker);
        } else {
          await removeFromWatchlist(change.ticker);
        }
      }
    }

    // Refresh portfolio and watchlist
    try {
      const [updatedPort, updatedWl, updatedHist] = await Promise.all([
        fetchPortfolio(),
        fetchWatchlist(),
        fetchPortfolioHistory(),
      ]);
      setPortfolio(updatedPort);
      setWatchlist(updatedWl);
      setPortfolioHistory(updatedHist);
    } catch (e) {
      console.error(e);
    }

    const assistantMsg: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: 'assistant',
      content: chatRes.message,
      actions: {
        trades: chatRes.trades,
        watchlist_changes: chatRes.watchlist_changes,
      },
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, assistantMsg]);
    setIsChatLoading(false);
  }, []);

  const currentSelectedData = watchlist.find((t) => t.ticker === selectedTicker);
  const currentSelectedPosition = portfolio.positions.find((p) => p.ticker === selectedTicker);

  return (
    <main className="flex-1 flex flex-col h-screen overflow-hidden bg-background">
      {/* Top Navigation / Status Header */}
      <Header portfolio={portfolio} connectionStatus={connectionStatus} />

      {/* Main Terminal Workspace Layout */}
      <div className="flex-1 flex overflow-hidden p-2 gap-2">
        {/* Left Column: Watchlist Panel */}
        <div className="w-64 lg:w-72 flex-shrink-0 flex flex-col">
          <WatchlistPanel
            watchlist={watchlist}
            selectedTicker={selectedTicker}
            onSelectTicker={setSelectedTicker}
            onAddTicker={handleAddTicker}
            onRemoveTicker={handleRemoveTicker}
            flashMap={flashMap}
          />
        </div>

        {/* Center Workspace Column */}
        <div className="flex-1 flex flex-col gap-2 min-w-0 overflow-y-auto">
          {/* Top Row: Main Chart & Heatmap */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-2 min-h-[300px] flex-shrink-0">
            <div className="xl:col-span-2">
              <MainChartArea
                tickerData={currentSelectedData}
                position={currentSelectedPosition}
              />
            </div>
            <div className="xl:col-span-1">
              <PortfolioHeatmap
                positions={portfolio.positions}
                onSelectTicker={setSelectedTicker}
              />
            </div>
          </div>

          {/* Instant Trade Bar */}
          <div className="flex-shrink-0">
            <TradeBar
              selectedTicker={selectedTicker}
              watchlist={watchlist}
              portfolio={portfolio}
              onExecuteTrade={handleExecuteTrade}
            />
          </div>

          {/* Bottom Row: Positions Table & Equity Chart */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-2 min-h-[220px] flex-1">
            <PositionsTable
              positions={portfolio.positions}
              selectedTicker={selectedTicker}
              onSelectTicker={setSelectedTicker}
              onQuickTrade={(ticker, side) => handleExecuteTrade(ticker, 1, side)}
            />
            <PnLChart
              history={portfolioHistory}
              currentValue={portfolio.total_value}
            />
          </div>
        </div>

        {/* Right Column: AI Chat Copilot Sidebar */}
        <AIChatSidebar
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isChatLoading}
        />
      </div>
    </main>
  );
}
