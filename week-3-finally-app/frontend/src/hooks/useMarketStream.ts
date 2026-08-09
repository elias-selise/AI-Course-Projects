import { useState, useEffect, useRef } from 'react';
import { PriceTick, StreamStatus } from '@/types';

export interface UseMarketStreamReturn {
  status: StreamStatus;
  prices: Record<string, PriceTick>;
  sparklines: Record<string, number[]>;
  flashes: Record<string, 'up' | 'down' | null>;
}

export function useMarketStream(
  streamUrl: string = '/api/stream/prices'
): UseMarketStreamReturn {
  const [status, setStatus] = useState<StreamStatus>('disconnected');
  const [prices, setPrices] = useState<Record<string, PriceTick>>({});
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({});
  const [flashes, setFlashes] = useState<Record<string, 'up' | 'down' | null>>({});

  const flashTimeouts = useRef<Record<string, NodeJS.Timeout>>({});

  useEffect(() => {
    setStatus('reconnecting');
    const eventSource = new EventSource(streamUrl);

    eventSource.onopen = () => {
      setStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        const tick: PriceTick = JSON.parse(event.data);
        const { ticker, price, direction } = tick;

        // 1. Update prices map
        setPrices((prev) => ({ ...prev, [ticker]: tick }));

        // 2. Append to rolling sparkline array (keep last 30 ticks)
        setSparklines((prev) => {
          const currentHistory = prev[ticker] || [];
          const updatedHistory = [...currentHistory, price].slice(-30);
          return { ...prev, [ticker]: updatedHistory };
        });

        // 3. Trigger 500ms flash animation if price changed
        if (direction === 'up' || direction === 'down') {
          setFlashes((prev) => ({ ...prev, [ticker]: direction }));

          if (flashTimeouts.current[ticker]) {
            clearTimeout(flashTimeouts.current[ticker]);
          }

          flashTimeouts.current[ticker] = setTimeout(() => {
            setFlashes((prev) => ({ ...prev, [ticker]: null }));
          }, 500);
        }
      } catch (err) {
        console.error('Failed to parse SSE price tick:', err);
      }
    };

    eventSource.onerror = () => {
      setStatus('reconnecting');
    };

    return () => {
      eventSource.close();
      setStatus('disconnected');
      Object.values(flashTimeouts.current).forEach(clearTimeout);
    };
  }, [streamUrl]);

  return { status, prices, sparklines, flashes };
}
