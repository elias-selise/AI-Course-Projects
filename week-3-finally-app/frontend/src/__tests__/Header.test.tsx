import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Header } from '../components/Header';
import { Portfolio } from '../types';

describe('Header Component', () => {
  const mockPortfolio: Portfolio = {
    cash_balance: 10000.0,
    total_value: 12500.0,
    unrealized_pnl: 2500.0,
    unrealized_pnl_pct: 25.0,
    positions: [],
  };

  it('renders branding title and subtitle', () => {
    render(<Header portfolio={mockPortfolio} connectionStatus="connected" />);
    expect(screen.getByText('FINALLY')).toBeInText();
    expect(screen.getByText('AI COPILOT')).toBeInText();
  });

  it('renders total portfolio value and cash balance', () => {
    render(<Header portfolio={mockPortfolio} connectionStatus="connected" />);
    expect(screen.getByText('$12,500.00')).toBeInText();
    expect(screen.getByText('$10,000.00')).toBeInText();
  });

  it('displays SSE connected status badge', () => {
    render(<Header portfolio={mockPortfolio} connectionStatus="connected" />);
    expect(screen.getByText('LIVE SSE')).toBeInText();
  });

  it('displays reconnecting status when offline', () => {
    render(<Header portfolio={mockPortfolio} connectionStatus="reconnecting" />);
    expect(screen.getByText('RECONNECTING')).toBeInText();
  });
});
