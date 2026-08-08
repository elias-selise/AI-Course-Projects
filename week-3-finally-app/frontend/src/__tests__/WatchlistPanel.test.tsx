import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { WatchlistPanel } from '../components/WatchlistPanel';
import { TickerData } from '../types';

describe('WatchlistPanel Component', () => {
  const mockWatchlist: TickerData[] = [
    { ticker: 'AAPL', name: 'Apple Inc.', price: 192.45, change_pct: 0.34, history: [190, 192.45] },
    { ticker: 'NVDA', name: 'NVIDIA Corp.', price: 128.50, change_pct: 3.63, history: [120, 128.50] },
  ];

  it('renders watchlist items', () => {
    render(
      <WatchlistPanel
        watchlist={mockWatchlist}
        selectedTicker="AAPL"
        onSelectTicker={vi.fn()}
        onAddTicker={vi.fn()}
        onRemoveTicker={vi.fn()}
      />
    );
    expect(screen.getByText('AAPL')).toBeInText();
    expect(screen.getByText('NVDA')).toBeInText();
    expect(screen.getByText('$192.45')).toBeInText();
  });

  it('calls onSelectTicker when a ticker is clicked', () => {
    const handleSelect = vi.fn();
    render(
      <WatchlistPanel
        watchlist={mockWatchlist}
        selectedTicker="AAPL"
        onSelectTicker={handleSelect}
        onAddTicker={vi.fn()}
        onRemoveTicker={vi.fn()}
      />
    );

    fireEvent.click(screen.getByText('NVDA'));
    expect(handleSelect).toHaveBeenCalledWith('NVDA');
  });

  it('submits new ticker to add', () => {
    const handleAdd = vi.fn();
    render(
      <WatchlistPanel
        watchlist={mockWatchlist}
        selectedTicker="AAPL"
        onSelectTicker={vi.fn()}
        onAddTicker={handleAdd}
        onRemoveTicker={vi.fn()}
      />
    );

    const input = screen.getByPlaceholderText('ADD TICKER');
    fireEvent.change(input, { target: { value: 'msft' } });
    fireEvent.click(screen.getByRole('button', { name: /add ticker/i }));

    expect(handleAdd).toHaveBeenCalledWith('MSFT');
  });
});
