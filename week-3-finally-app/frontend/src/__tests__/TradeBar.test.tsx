import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TradeBar } from '../components/TradeBar';
import { Portfolio, TickerData } from '../types';

describe('TradeBar Component', () => {
  const mockWatchlist: TickerData[] = [
    { ticker: 'AAPL', price: 200.0, change_pct: 1.0, history: [200] },
  ];

  const mockPortfolio: Portfolio = {
    cash_balance: 10000.0,
    total_value: 10000.0,
    unrealized_pnl: 0,
    unrealized_pnl_pct: 0,
    positions: [],
  };

  it('renders buy/sell toggle and order button', () => {
    render(
      <TradeBar
        selectedTicker="AAPL"
        watchlist={mockWatchlist}
        portfolio={mockPortfolio}
        onExecuteTrade={vi.fn().mockResolvedValue({ success: true, message: 'Executed' })}
      />
    );

    expect(screen.getByText('BUY')).toBeInText();
    expect(screen.getByText('SELL')).toBeInText();
    expect(screen.getByText(/EXECUTE BUY 1 AAPL/i)).toBeInText();
  });

  it('calculates order cost dynamically based on quantity', () => {
    render(
      <TradeBar
        selectedTicker="AAPL"
        watchlist={mockWatchlist}
        portfolio={mockPortfolio}
        onExecuteTrade={vi.fn().mockResolvedValue({ success: true, message: 'Executed' })}
      />
    );

    const qtyInput = screen.getByDisplayValue('1');
    fireEvent.change(qtyInput, { target: { value: '5' } });

    // 5 * $200 = $1,000.00
    expect(screen.getByText('$1,000.00')).toBeInText();
  });

  it('calls onExecuteTrade when form submitted', async () => {
    const handleTrade = vi.fn().mockResolvedValue({ success: true, message: 'Bought 1 AAPL' });

    render(
      <TradeBar
        selectedTicker="AAPL"
        watchlist={mockWatchlist}
        portfolio={mockPortfolio}
        onExecuteTrade={handleTrade}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /EXECUTE BUY/i }));

    await waitFor(() => {
      expect(handleTrade).toHaveBeenCalledWith('AAPL', 1, 'buy');
    });
  });
});
