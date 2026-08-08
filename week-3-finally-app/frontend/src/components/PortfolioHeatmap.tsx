'use client';

import React from 'react';
import { ResponsiveContainer, Treemap } from 'recharts';
import { useTerminalStore } from '@/store/useTerminalStore';

interface TreemapNodeProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  name?: string;
  size?: number;
  pnl?: number;
  pnlPercent?: number;
}

const CustomizedTreemapContent: React.FC<TreemapNodeProps> = ({
  x = 0,
  y = 0,
  width = 0,
  height = 0,
  name,
  pnlPercent = 0,
}) => {
  if (width < 20 || height < 20) return null;

  const isCash = name === 'CASH';
  const isPositive = pnlPercent >= 0;

  let bgFill = '#334155'; // Cash/neutral
  if (!isCash) {
    bgFill = isPositive ? '#15803d' : '#b91c1c';
  }

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: bgFill,
          stroke: '#0d1117',
          strokeWidth: 2,
          rx: 4,
        }}
      />
      {width > 40 && height > 30 && (
        <text
          x={x + width / 2}
          y={y + height / 2 - 4}
          textAnchor="middle"
          fill="#ffffff"
          fontSize={11}
          fontWeight="bold"
          fontFamily="monospace"
        >
          {name}
        </text>
      )}
      {width > 40 && height > 45 && !isCash && (
        <text
          x={x + width / 2}
          y={y + height / 2 + 10}
          textAnchor="middle"
          fill={isPositive ? '#86efac' : '#fca5a5'}
          fontSize={10}
          fontFamily="monospace"
        >
          {isPositive ? '+' : ''}
          {pnlPercent.toFixed(1)}%
        </text>
      )}
    </g>
  );
};

export const PortfolioHeatmap: React.FC = () => {
  const { portfolio } = useTerminalStore();

  const positions = portfolio?.positions || [];
  const cash = portfolio?.cash_balance || 0;

  const treeData = [
    ...positions.map((pos) => ({
      name: pos.ticker,
      size: Math.max(pos.market_value, 1),
      pnl: pos.unrealized_pnl,
      pnlPercent: pos.unrealized_pnl_percent,
    })),
    ...(cash > 0
      ? [
          {
            name: 'CASH',
            size: cash,
            pnl: 0,
            pnlPercent: 0,
          },
        ]
      : []),
  ];

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 flex flex-col h-full">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-terminal-yellow mb-2">
        Portfolio Allocation & P&L Heatmap
      </h2>

      <div className="w-full h-[220px] min-h-[220px] relative">
        {treeData.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-terminal-muted text-xs font-mono">
            No active portfolio positions
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={treeData}
              dataKey="size"
              aspectRatio={4 / 3}
              stroke="#0d1117"
              content={<CustomizedTreemapContent />}
            />
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
