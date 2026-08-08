'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import { useTerminalStore } from '@/store/useTerminalStore';

export const PortfolioPnLChart: React.FC = () => {
  const { history, portfolio } = useTerminalStore();

  const formattedData = history.map((snap) => {
    const dateObj = new Date(snap.recorded_at);
    const timeStr = isNaN(dateObj.getTime())
      ? snap.recorded_at
      : dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return {
      time: timeStr,
      value: snap.total_value,
    };
  });

  const latestVal = portfolio?.total_value ?? 10000;
  const isProfitable = latestVal >= 10000;
  const lineColor = isProfitable ? '#22c55e' : '#ef4444';

  const values = formattedData.map((d) => d.value);
  const minVal = values.length ? Math.floor(Math.min(...values) * 0.99) : 9000;
  const maxVal = values.length ? Math.ceil(Math.max(...values) * 1.01) : 11000;

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-terminal-yellow">
          Portfolio Valuation Timeline
        </h2>
        <span className={`text-xs font-mono font-bold ${isProfitable ? 'text-emerald-400' : 'text-red-400'}`}>
          ${latestVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      </div>

      <div className="w-full h-[220px] min-h-[220px] relative">
        {formattedData.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-terminal-muted text-xs font-mono">
            No history snapshots recorded yet...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={formattedData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey="time" stroke="#4b5563" tick={{ fontSize: 10 }} />
              <YAxis
                domain={[minVal, maxVal]}
                stroke="#4b5563"
                tick={{ fontSize: 10 }}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  borderColor: '#21262d',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
                formatter={(val: number) => [`$${val.toFixed(2)}`, 'Portfolio Value']}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={lineColor}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
