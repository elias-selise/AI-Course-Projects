import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  fetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  fetchPortfolio,
  executeTrade,
  sendChatMessage,
} from '../services/api';

describe('API Service Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches initial watchlist (mock or live)', async () => {
    const watchlist = await fetchWatchlist();
    expect(Array.isArray(watchlist)).toBe(true);
    expect(watchlist.length).toBeGreaterThan(0);
    expect(watchlist[0]).toHaveProperty('ticker');
    expect(watchlist[0]).toHaveProperty('price');
  });

  it('adds a new ticker to watchlist', async () => {
    const res = await addToWatchlist('TSLA');
    expect(res.success).toBe(true);
    expect(res.watchlist).toBeDefined();
  });

  it('removes a ticker from watchlist', async () => {
    const res = await removeFromWatchlist('TSLA');
    expect(res.success).toBe(true);
  });

  it('fetches portfolio data correctly', async () => {
    const portfolio = await fetchPortfolio();
    expect(portfolio).toHaveProperty('cash_balance');
    expect(portfolio).toHaveProperty('total_value');
    expect(portfolio).toHaveProperty('positions');
  });

  it('executes a buy trade successfully', async () => {
    const tradeRes = await executeTrade('AAPL', 2, 'buy');
    expect(tradeRes.success).toBe(true);
    expect(tradeRes.message).toContain('AAPL');
  });

  it('handles invalid sell trade gracefully', async () => {
    const tradeRes = await executeTrade('NONEXISTENT', 1000, 'sell');
    expect(tradeRes.success).toBe(false);
    expect(tradeRes.message).toBeDefined();
  });

  it('processes chat messages and generates response', async () => {
    const chatRes = await sendChatMessage('Analyze my portfolio');
    expect(chatRes.message).toBeDefined();
    expect(typeof chatRes.message).toBe('string');
  });
});
