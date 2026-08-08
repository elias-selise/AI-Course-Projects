import {
  Portfolio,
  PortfolioSnapshot,
  WatchlistItem,
  TradeRequest,
  ChatMessage,
} from '@/types';

const BASE_URL = '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(`API Error (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function getPortfolio(): Promise<Portfolio> {
  return fetchJSON<Portfolio>('/api/portfolio');
}

export async function executeTrade(trade: TradeRequest): Promise<any> {
  return fetchJSON<any>('/api/portfolio/trade', {
    method: 'POST',
    body: JSON.stringify(trade),
  });
}

export async function getPortfolioHistory(): Promise<PortfolioSnapshot[]> {
  return fetchJSON<PortfolioSnapshot[]>('/api/portfolio/history');
}

export async function getWatchlist(): Promise<WatchlistItem[]> {
  return fetchJSON<WatchlistItem[]>('/api/watchlist');
}

export async function addWatchlist(ticker: string): Promise<any> {
  return fetchJSON<any>('/api/watchlist', {
    method: 'POST',
    body: JSON.stringify({ ticker }),
  });
}

export async function deleteWatchlist(ticker: string): Promise<any> {
  return fetchJSON<any>(`/api/watchlist/${encodeURIComponent(ticker)}`, {
    method: 'DELETE',
  });
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  return fetchJSON<ChatMessage[]>('/api/chat/history');
}

export async function sendChatMessage(message: string): Promise<any> {
  return fetchJSON<any>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}
