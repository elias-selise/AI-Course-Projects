import { useEffect, useState, useRef, useCallback } from 'react';
import { ConnectionStatus, TickerData } from '../types';

export interface PriceUpdatePayload {
  ticker: string;
  price: number;
  prev_price?: number;
  change_pct?: number;
  timestamp?: string;
}

export function useSSE(
  onPriceUpdate?: (update: PriceUpdatePayload | PriceUpdatePayload[]) => void
) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const mockTimerRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef<number>(0);
  const onPriceUpdateRef = useRef(onPriceUpdate);

  useEffect(() => {
    onPriceUpdateRef.current = onPriceUpdate;
  }, [onPriceUpdate]);

  const startMockSimulation = useCallback(() => {
    setStatus('connected');
    if (mockTimerRef.current) clearInterval(mockTimerRef.current);

    const tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX'];

    mockTimerRef.current = setInterval(() => {
      // Pick 1-3 random tickers to fluctuate
      const count = Math.floor(Math.random() * 3) + 1;
      const updates: PriceUpdatePayload[] = [];

      for (let i = 0; i < count; i++) {
        const ticker = tickers[Math.floor(Math.random() * tickers.length)];
        const percentChange = (Math.random() - 0.49) * 0.015; // -0.7% to +0.8%
        updates.push({
          ticker,
          price: 0, // Consumer will apply delta relative to last known price
          change_pct: Number((percentChange * 100).toFixed(2)),
          timestamp: new Date().toISOString(),
        });
      }

      if (onPriceUpdateRef.current && updates.length > 0) {
        onPriceUpdateRef.current(updates);
      }
    }, 1500);
  }, []);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setStatus('reconnecting');

    try {
      const es = new EventSource('/api/stream/prices');
      eventSourceRef.current = es;

      es.onopen = () => {
        setStatus('connected');
        retryCountRef.current = 0;
      };

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onPriceUpdateRef.current) {
            onPriceUpdateRef.current(data);
          }
        } catch (e) {
          console.error('Failed to parse SSE price data:', e);
        }
      };

      es.onerror = () => {
        es.close();
        setStatus('reconnecting');
        retryCountRef.current += 1;

        if (retryCountRef.current > 2) {
          startMockSimulation();
        } else {
          const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (e) {
      startMockSimulation();
    }
  }, [startMockSimulation]);

  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (mockTimerRef.current) {
        clearInterval(mockTimerRef.current);
      }
    };
  }, [connect]);

  return { status, reconnect: connect };
}
