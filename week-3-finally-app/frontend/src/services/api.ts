import { Portfolio, PortfolioSnapshot, TickerData, TradeResponse, ChatResponse } from '../types';

const API_BASE = '/api';

// Initial fallback mock data for offline/standalone mode
const DEFAULT_TICKERS: TickerData[] = [
  { ticker: 'AAPL', name: 'Apple Inc.', price: 192.45, prev_price: 191.80, change_pct: 0.34, history: [189.5, 190.2, 191.0, 190.8, 191.8, 192.45] },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', price: 175.20, prev_price: 175.46, change_pct: -0.15, history: [176.0, 175.8, 176.2, 175.5, 175.46, 175.20] },
  { ticker: 'MSFT', name: 'Microsoft Corp.', price: 448.90, prev_price: 445.10, change_pct: 0.85, history: [442.0, 444.0, 445.0, 443.5, 445.1, 448.90] },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', price: 186.30, prev_price: 184.20, change_pct: 1.14, history: [182.0, 183.5, 184.0, 184.2, 186.30] },
  { ticker: 'TSLA', name: 'Tesla Inc.', price: 215.80, prev_price: 221.00, change_pct: -2.35, history: [224.0, 222.5, 221.0, 218.0, 215.80] },
  { ticker: 'NVDA', name: 'NVIDIA Corp.', price: 128.50, prev_price: 124.00, change_pct: 3.63, history: [122.0, 123.5, 124.0, 126.0, 128.50] },
  { ticker: 'META', name: 'Meta Platforms Inc.', price: 512.40, prev_price: 508.90, change_pct: 0.69, history: [505.0, 506.8, 508.9, 510.2, 512.40] },
  { ticker: 'JPM', name: 'JPMorgan Chase & Co.', price: 208.15, prev_price: 207.50, change_pct: 0.31, history: [206.5, 207.0, 207.5, 208.15] },
  { ticker: 'V', name: 'Visa Inc.', price: 268.40, prev_price: 269.10, change_pct: -0.26, history: [270.0, 269.5, 269.1, 268.40] },
  { ticker: 'NFLX', name: 'Netflix Inc.', price: 654.20, prev_price: 648.00, change_pct: 0.96, history: [642.0, 645.0, 648.0, 654.20] },
];

const INITIAL_MOCK_PORTFOLIO: Portfolio = {
  cash_balance: 10000.0,
  total_value: 12543.50,
  unrealized_pnl: 2543.50,
  unrealized_pnl_pct: 25.43,
  positions: [
    {
      id: 'pos-1',
      ticker: 'AAPL',
      quantity: 10,
      avg_cost: 180.00,
      current_price: 192.45,
      market_value: 1924.50,
      unrealized_pnl: 124.50,
      unrealized_pnl_pct: 6.92,
    },
    {
      id: 'pos-2',
      ticker: 'NVDA',
      quantity: 20,
      avg_cost: 110.00,
      current_price: 128.50,
      market_value: 2570.00,
      unrealized_pnl: 370.00,
      unrealized_pnl_pct: 16.82,
    },
    {
      id: 'pos-3',
      ticker: 'TSLA',
      quantity: 5,
      avg_cost: 230.00,
      current_price: 215.80,
      market_value: 1079.00,
      unrealized_pnl: -71.00,
      unrealized_pnl_pct: -6.17,
    },
  ],
};

let mockPortfolioState = { ...INITIAL_MOCK_PORTFOLIO };
let mockWatchlistState = [...DEFAULT_TICKERS];

export async function fetchWatchlist(): Promise<TickerData[]> {
  try {
    const res = await fetch(`${API_BASE}/watchlist`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (Array.isArray(data)) {
      return data.map((item: any) => {
        const price = item.price ?? item.current_price ?? item.price_update?.price ?? 100.0;
        const prevPrice = item.prev_price ?? item.price_update?.previous_price ?? price;
        const change_pct = item.change_pct ?? (prevPrice > 0 ? ((price - prevPrice) / prevPrice) * 100 : 0.0);
        return {
          ticker: item.ticker,
          name: item.name || `${item.ticker} Inc.`,
          price,
          prev_price: prevPrice,
          change_pct,
          history: item.history && item.history.length > 0 ? item.history : [price],
        };
      });
    }
    return data;
  } catch (err) {
    return mockWatchlistState;
  }
}

export async function addToWatchlist(ticker: string): Promise<{ success: boolean; watchlist?: TickerData[]; error?: string }> {
  const upper = ticker.toUpperCase().trim();
  if (!upper) return { success: false, error: 'Invalid ticker symbol' };
  
  try {
    const res = await fetch(`${API_BASE}/watchlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: upper }),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    return { success: true, watchlist: data.watchlist || data };
  } catch (err: any) {
    // Mock fallback
    if (!mockWatchlistState.some(t => t.ticker === upper)) {
      const newTicker: TickerData = {
        ticker: upper,
        price: 100.0,
        change_pct: 0.0,
        history: [100.0],
      };
      mockWatchlistState = [...mockWatchlistState, newTicker];
    }
    return { success: true, watchlist: mockWatchlistState };
  }
}

export async function removeFromWatchlist(ticker: string): Promise<{ success: boolean; watchlist?: TickerData[]; error?: string }> {
  const upper = ticker.toUpperCase().trim();
  try {
    const res = await fetch(`${API_BASE}/watchlist/${upper}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, watchlist: data.watchlist || data };
  } catch (err) {
    mockWatchlistState = mockWatchlistState.filter(t => t.ticker !== upper);
    return { success: true, watchlist: mockWatchlistState };
  }
}

export async function fetchPortfolio(): Promise<Portfolio> {
  try {
    const res = await fetch(`${API_BASE}/portfolio`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    const total_value = data.total_value ?? data.total_portfolio_value ?? 10000.0;
    const unrealized_pnl = data.unrealized_pnl ?? data.total_unrealized_pnl ?? 0.0;
    const positions = data.positions || [];

    let unrealized_pnl_pct = data.unrealized_pnl_pct ?? 0.0;
    if (data.unrealized_pnl_pct === undefined && positions.length > 0) {
      const posCost = positions.reduce((sum: number, p: any) => sum + (p.quantity * p.avg_cost), 0);
      if (posCost > 0) {
        unrealized_pnl_pct = (unrealized_pnl / posCost) * 100;
      }
    }

    return {
      cash_balance: data.cash_balance ?? 10000.0,
      total_value,
      unrealized_pnl,
      unrealized_pnl_pct,
      positions,
    };
  } catch (err) {
    return mockPortfolioState;
  }
}

export async function executeTrade(ticker: string, quantity: number, side: 'buy' | 'sell'): Promise<TradeResponse> {
  const upper = ticker.toUpperCase().trim();
  if (!upper || quantity <= 0) {
    return { success: false, message: 'Invalid ticker or quantity' };
  }

  try {
    const res = await fetch(`${API_BASE}/portfolio/trade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: upper, quantity, side }),
    });
    const data = await res.json();
    if (!res.ok) {
      return { success: false, message: data.detail || data.message || 'Trade failed' };
    }
    return data;
  } catch (err) {
    // Local mock trade execution logic for standalone mode
    const currentPrice = mockWatchlistState.find(t => t.ticker === upper)?.price || 150.0;
    const totalCost = currentPrice * quantity;

    if (side === 'buy') {
      if (mockPortfolioState.cash_balance < totalCost) {
        return { success: false, message: `Insufficient cash balance. Required: $${totalCost.toFixed(2)}, Available: $${mockPortfolioState.cash_balance.toFixed(2)}` };
      }
      
      mockPortfolioState.cash_balance -= totalCost;
      const existingIndex = mockPortfolioState.positions.findIndex(p => p.ticker === upper);
      if (existingIndex >= 0) {
        const existing = mockPortfolioState.positions[existingIndex];
        const newQty = existing.quantity + quantity;
        const newAvgCost = ((existing.quantity * existing.avg_cost) + totalCost) / newQty;
        mockPortfolioState.positions[existingIndex] = {
          ...existing,
          quantity: newQty,
          avg_cost: newAvgCost,
          current_price: currentPrice,
          market_value: newQty * currentPrice,
          unrealized_pnl: (currentPrice - newAvgCost) * newQty,
          unrealized_pnl_pct: ((currentPrice - newAvgCost) / newAvgCost) * 100,
        };
      } else {
        mockPortfolioState.positions.push({
          id: `pos-${Date.now()}`,
          ticker: upper,
          quantity,
          avg_cost: currentPrice,
          current_price: currentPrice,
          market_value: totalCost,
          unrealized_pnl: 0,
          unrealized_pnl_pct: 0,
        });
      }
    } else {
      // Sell
      const existingIndex = mockPortfolioState.positions.findIndex(p => p.ticker === upper);
      if (existingIndex < 0 || mockPortfolioState.positions[existingIndex].quantity < quantity) {
        const owned = existingIndex >= 0 ? mockPortfolioState.positions[existingIndex].quantity : 0;
        return { success: false, message: `Insufficient position in ${upper}. Owned: ${owned}, Requested: ${quantity}` };
      }

      const existing = mockPortfolioState.positions[existingIndex];
      mockPortfolioState.cash_balance += totalCost;
      const remainingQty = existing.quantity - quantity;
      
      if (remainingQty <= 0) {
        mockPortfolioState.positions.splice(existingIndex, 1);
      } else {
        mockPortfolioState.positions[existingIndex] = {
          ...existing,
          quantity: remainingQty,
          market_value: remainingQty * currentPrice,
          unrealized_pnl: (currentPrice - existing.avg_cost) * remainingQty,
          unrealized_pnl_pct: ((currentPrice - existing.avg_cost) / existing.avg_cost) * 100,
        };
      }
    }

    // Recalculate totals
    const posValue = mockPortfolioState.positions.reduce((sum, p) => sum + p.market_value, 0);
    const posCost = mockPortfolioState.positions.reduce((sum, p) => sum + (p.quantity * p.avg_cost), 0);
    mockPortfolioState.total_value = mockPortfolioState.cash_balance + posValue;
    mockPortfolioState.unrealized_pnl = posValue - posCost;
    mockPortfolioState.unrealized_pnl_pct = posCost > 0 ? (mockPortfolioState.unrealized_pnl / posCost) * 100 : 0;

    return {
      success: true,
      message: `Executed ${side.toUpperCase()} ${quantity} shares of ${upper} @ $${currentPrice.toFixed(2)}`,
      portfolio: mockPortfolioState,
      trade: {
        id: `trd-${Date.now()}`,
        ticker: upper,
        side,
        quantity,
        price: currentPrice,
        executed_at: new Date().toISOString(),
      },
    };
  }
}

export async function fetchPortfolioHistory(): Promise<PortfolioSnapshot[]> {
  try {
    const res = await fetch(`${API_BASE}/portfolio/history`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    // Generate realistic historical snapshots
    const now = Date.now();
    const snapshots: PortfolioSnapshot[] = [];
    let baseValue = 10000.0;
    
    for (let i = 20; i >= 0; i--) {
      const timestamp = new Date(now - i * 300000).toISOString(); // 5 min intervals
      if (i === 20) baseValue = 10000.0;
      else {
        const change = (Math.random() - 0.45) * 80;
        baseValue = Math.max(9000, baseValue + change);
      }
      snapshots.push({
        id: `snap-${i}`,
        recorded_at: timestamp,
        total_value: Number(baseValue.toFixed(2)),
      });
    }
    return snapshots;
  }
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    return data;
  } catch (err: any) {
    // Fallback Mock Assistant Response
    const lower = message.toLowerCase();
    let reply = "I've analyzed your request and current portfolio position.";
    let trades: ChatResponse['trades'] = [];
    let watchlist_changes: ChatResponse['watchlist_changes'] = [];

    if (lower.includes('buy')) {
      const qtyMatch = lower.match(/\b(\d+)\b/);
      const qty = qtyMatch ? parseInt(qtyMatch[1]) : 5;
      const knownTickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX', 'AMD', 'PYPL'];
      const foundTicker = knownTickers.find(t => lower.includes(t.toLowerCase()));
      const ticker = foundTicker || 'MSFT';
      trades.push({ ticker, side: 'buy', quantity: qty });
      reply = `Executing a market order to BUY ${qty} shares of ${ticker}. The order has been processed at current market price.`;
    } else if (lower.includes('sell')) {
      const qtyMatch = lower.match(/\b(\d+)\b/);
      const qty = qtyMatch ? parseInt(qtyMatch[1]) : 5;
      const knownTickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX', 'AMD', 'PYPL'];
      const foundTicker = knownTickers.find(t => lower.includes(t.toLowerCase()));
      const ticker = foundTicker || 'AAPL';
      trades.push({ ticker, side: 'sell', quantity: qty });
      reply = `Executing a market order to SELL ${qty} shares of ${ticker}. Profits/Losses have been realized into your cash balance.`;
    } else if (lower.includes('add') || lower.includes('watch')) {
      const match = lower.match(/(?:add|watch)\s+([a-z]+)/i);
      const ticker = match && match[1] ? match[1].toUpperCase() : 'AMD';
      watchlist_changes.push({ ticker, action: 'add' });
      reply = `Added ${ticker} to your watchlist. You can now monitor its live price fluctuations and sparkline history.`;
    } else if (lower.includes('performance') || lower.includes('portfolio') || lower.includes('analyze')) {
      reply = `Your portfolio currently holds $${mockPortfolioState.cash_balance.toFixed(2)} in cash and $${(mockPortfolioState.total_value - mockPortfolioState.cash_balance).toFixed(2)} in active positions. Total unrealized P&L is ${mockPortfolioState.unrealized_pnl >= 0 ? '+' : ''}$${mockPortfolioState.unrealized_pnl.toFixed(2)} (${mockPortfolioState.unrealized_pnl_pct.toFixed(2)}%). Top allocation is currently NVDA.`;
    }

    return {
      message: reply,
      trades,
      watchlist_changes,
    };
  }
}

export async function checkHealth(): Promise<{ status: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline' };
  }
}
