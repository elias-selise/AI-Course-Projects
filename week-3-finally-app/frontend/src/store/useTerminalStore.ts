import { create } from 'zustand';
import { Portfolio, WatchlistItem, ChatMessage, PortfolioSnapshot } from '@/types';
import * as api from '@/lib/api';

interface TerminalStore {
  selectedTicker: string;
  portfolio: Portfolio | null;
  watchlist: WatchlistItem[];
  history: PortfolioSnapshot[];
  chatHistory: ChatMessage[];
  isLoadingChat: boolean;

  setSelectedTicker: (ticker: string) => void;
  fetchPortfolio: () => Promise<void>;
  fetchWatchlist: () => Promise<void>;
  fetchHistory: () => Promise<void>;
  fetchChatHistory: () => Promise<void>;
  refreshAll: () => Promise<void>;
  sendChatMessage: (message: string) => Promise<void>;
  executeTrade: (ticker: string, side: 'buy' | 'sell', quantity: number) => Promise<void>;
  addWatchlistTicker: (ticker: string) => Promise<void>;
  removeWatchlistTicker: (ticker: string) => Promise<void>;
}

export const useTerminalStore = create<TerminalStore>((set, get) => ({
  selectedTicker: 'AAPL',
  portfolio: null,
  watchlist: [],
  history: [],
  chatHistory: [],
  isLoadingChat: false,

  setSelectedTicker: (ticker: string) => set({ selectedTicker: ticker.toUpperCase() }),

  fetchPortfolio: async () => {
    try {
      const portfolio = await api.getPortfolio();
      set({ portfolio });
    } catch (err) {
      console.error('Error fetching portfolio:', err);
    }
  },

  fetchWatchlist: async () => {
    try {
      const watchlist = await api.getWatchlist();
      set({ watchlist });
    } catch (err) {
      console.error('Error fetching watchlist:', err);
    }
  },

  fetchHistory: async () => {
    try {
      const history = await api.getPortfolioHistory();
      set({ history });
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  },

  fetchChatHistory: async () => {
    try {
      const chatHistory = await api.getChatHistory();
      set({ chatHistory });
    } catch (err) {
      console.error('Error fetching chat history:', err);
    }
  },

  refreshAll: async () => {
    await Promise.all([get().fetchPortfolio(), get().fetchWatchlist(), get().fetchHistory()]);
  },

  sendChatMessage: async (message: string) => {
    set({ isLoadingChat: true });
    try {
      await api.sendChatMessage(message);
      await Promise.all([
        get().fetchChatHistory(),
        get().fetchPortfolio(),
        get().fetchWatchlist(),
        get().fetchHistory(),
      ]);
    } catch (err) {
      console.error('Error sending chat message:', err);
    } finally {
      set({ isLoadingChat: false });
    }
  },

  executeTrade: async (ticker: string, side: 'buy' | 'sell', quantity: number) => {
    try {
      await api.executeTrade({ ticker, side, quantity });
      await get().refreshAll();
    } catch (err) {
      console.error('Error executing trade:', err);
      throw err;
    }
  },

  addWatchlistTicker: async (ticker: string) => {
    try {
      await api.addWatchlist(ticker);
      await get().fetchWatchlist();
    } catch (err) {
      console.error('Error adding watchlist ticker:', err);
    }
  },

  removeWatchlistTicker: async (ticker: string) => {
    try {
      await api.deleteWatchlist(ticker);
      await get().fetchWatchlist();
    } catch (err) {
      console.error('Error removing watchlist ticker:', err);
    }
  },
}));
