import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AIChatSidebar } from '../components/AIChatSidebar';
import { ChatMessage } from '../types';

describe('AIChatSidebar Component', () => {
  const mockMessages: ChatMessage[] = [
    {
      id: 'm1',
      role: 'user',
      content: 'Buy 5 shares of AAPL',
      timestamp: new Date().toISOString(),
    },
    {
      id: 'm2',
      role: 'assistant',
      content: 'I have executed your order for 5 shares of AAPL.',
      actions: {
        trades: [{ ticker: 'AAPL', side: 'buy', quantity: 5, price: 192.45 }],
      },
      timestamp: new Date().toISOString(),
    },
  ];

  it('renders chat message history and inline trade action badges', () => {
    render(
      <AIChatSidebar
        messages={mockMessages}
        onSendMessage={vi.fn().mockResolvedValue(undefined)}
        isLoading={false}
      />
    );

    expect(screen.getByText('Buy 5 shares of AAPL')).toBeInText();
    expect(screen.getByText('I have executed your order for 5 shares of AAPL.')).toBeInText();
    expect(screen.getByText(/AUTO-EXECUTED: BUY 5 AAPL @ $192.45/i)).toBeInText();
  });

  it('submits user message on form submit', () => {
    const handleSend = vi.fn().mockResolvedValue(undefined);
    render(
      <AIChatSidebar
        messages={mockMessages}
        onSendMessage={handleSend}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Ask AI to analyze/i);
    fireEvent.change(input, { target: { value: 'Analyze my risk' } });
    fireEvent.submit(input.closest('form')!);

    expect(handleSend).toHaveBeenCalledWith('Analyze my risk');
  });

  it('renders loading state when AI is processing', () => {
    render(
      <AIChatSidebar
        messages={mockMessages}
        onSendMessage={vi.fn().mockResolvedValue(undefined)}
        isLoading={true}
      />
    );

    expect(screen.getByText(/FINALLY AI IS THINKING.../i)).toBeInText();
  });
});
