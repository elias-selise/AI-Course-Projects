export type Side = 'buy' | 'sell';

export interface TickerData {
  ticker: string;
  name?: string;
  price: number;
  prev_price?: number;
  change_pct: number;
  timestamp?: string;
  history: number[]; // Accumulated sparkline price history
}

export interface Position {
  id: string;
  user_id?: string;
  ticker: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  updated_at?: string;
}

export interface Portfolio {
  cash_balance: number;
  total_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  positions: Position[];
}

export interface PortfolioSnapshot {
  id?: string;
  total_value: number;
  recorded_at: string;
}

export interface Trade {
  id: string;
  ticker: string;
  side: Side;
  quantity: number;
  price: number;
  executed_at: string;
}

export interface TradeAction {
  ticker: string;
  side: Side;
  quantity: number;
  price?: number;
}

export interface WatchlistAction {
  ticker: string;
  action: 'add' | 'remove';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  actions?: {
    trades?: TradeAction[];
    watchlist_changes?: WatchlistAction[];
  };
  timestamp: string;
}

export type ConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';

export interface TradeResponse {
  success: boolean;
  message: string;
  trade?: Trade;
  portfolio?: Portfolio;
  error?: string;
}

export interface ChatResponse {
  message: string;
  trades?: TradeAction[];
  watchlist_changes?: WatchlistAction[];
  error?: string;
}
