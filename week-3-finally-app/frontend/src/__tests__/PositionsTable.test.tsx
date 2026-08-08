import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PositionsTable } from '../components/PositionsTable';
import { Position } from '../types';

describe('PositionsTable Component', () => {
  const mockPositions: Position[] = [
    {
      id: 'pos-1',
      ticker: 'AAPL',
      quantity: 10,
      avg_cost: 180.0,
      current_price: 192.45,
      market_value: 1924.5,
      unrealized_pnl: 124.5,
      unrealized_pnl_pct: 6.92,
    },
  ];

  it('renders positions table rows', () => {
    render(
      <PositionsTable
        positions={mockPositions}
        selectedTicker="AAPL"
        onSelectTicker={vi.fn()}
      />
    );

    expect(screen.getByText('AAPL')).toBeInText();
    expect(screen.getByText('10')).toBeInText();
    expect(screen.getByText('$1,924.50')).toBeInText();
    expect(screen.getByText('+$124.50')).toBeInText();
  });

  it('shows empty message when no positions', () => {
    render(
      <PositionsTable
        positions={[]}
        selectedTicker="AAPL"
        onSelectTicker={vi.fn()}
      />
    );

    expect(screen.getByText('NO OPEN POSITIONS HELD')).toBeInText();
  });

  it('triggers quick trade callbacks', () => {
    const handleQuickTrade = vi.fn();
    render(
      <PositionsTable
        positions={mockPositions}
        selectedTicker="AAPL"
        onSelectTicker={vi.fn()}
        onQuickTrade={handleQuickTrade}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: 'BUY' }));
    expect(handleQuickTrade).toHaveBeenCalledWith('AAPL', 'buy');
  });
});
