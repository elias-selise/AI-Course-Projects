export type StreamStatus = 'connected' | 'reconnecting' | 'disconnected';

export interface PriceTick {
  ticker: string;
  price: number;
  previous_price: number;
  change: number;
  direction: 'up' | 'down' | 'flat';
  timestamp: string;
}

export interface Position {
  ticker: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
}

export interface Portfolio {
  cash_balance: number;
  positions_value: number;
  total_value: number;
  total_unrealized_pnl: number;
  total_unrealized_pnl_percent: number;
  positions: Position[];
}

export interface PortfolioSnapshot {
  id: string;
  total_value: number;
  recorded_at: string;
}

export interface WatchlistItem {
  id: string;
  ticker: string;
  price: number;
  previous_price: number;
  change: number;
  direction: 'up' | 'down' | 'flat';
  added_at: string;
}

export interface TradeRequest {
  ticker: string;
  side: 'buy' | 'sell';
  quantity: number;
}

export interface ExecutedAction {
  trades?: Array<{
    ticker: string;
    side: 'buy' | 'sell';
    quantity: number;
    price: number;
    status: 'success' | 'failed';
    error?: string;
  }>;
  watchlist_changes?: Array<{
    ticker: string;
    action: 'add' | 'remove';
    status: 'success' | 'failed';
    error?: string;
  }>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  actions?: ExecutedAction | null;
  created_at: string;
}
