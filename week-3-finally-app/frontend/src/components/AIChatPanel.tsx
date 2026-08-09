'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { ExecutedAction } from '@/types';
import { Bot, Send, User, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const ActionCards: React.FC<{ actions?: ExecutedAction | null }> = ({ actions }) => {
  if (!actions) return null;

  const hasTrades = actions.trades && actions.trades.length > 0;
  const hasWatchlist = actions.watchlist_changes && actions.watchlist_changes.length > 0;

  if (!hasTrades && !hasWatchlist) return null;

  return (
    <div className="mt-2 space-y-1.5">
      {/* Executed Trades */}
      {hasTrades &&
        actions.trades!.map((trade, idx) => (
          <div
            key={idx}
            className="p-2 rounded bg-terminal-bg/80 border border-terminal-purple/50 flex items-center justify-between text-[11px] font-mono"
          >
            <div>
              <span className="font-bold text-white uppercase">{trade.side}</span>{' '}
              <span className="text-terminal-yellow font-bold">{trade.quantity}</span> sh of{' '}
              <span className="font-bold text-white">{trade.ticker}</span>
              {trade.price > 0 && <span className="text-terminal-muted"> @ ${trade.price.toFixed(2)}</span>}
            </div>
            {trade.status === 'success' ? (
              <span className="flex items-center text-emerald-400 font-semibold text-[10px]">
                <CheckCircle2 className="w-3 h-3 mr-0.5" /> EXECUTED
              </span>
            ) : (
              <span className="flex items-center text-red-400 font-semibold text-[10px]">
                <AlertCircle className="w-3 h-3 mr-0.5" /> FAILED
              </span>
            )}
          </div>
        ))}

      {/* Watchlist Changes */}
      {hasWatchlist &&
        actions.watchlist_changes!.map((item, idx) => (
          <div
            key={idx}
            className="p-2 rounded bg-terminal-bg/80 border border-terminal-blue/50 flex items-center justify-between text-[11px] font-mono"
          >
            <div>
              <span className="font-bold text-white uppercase">WATCHLIST {item.action}</span>:{' '}
              <span className="font-bold text-terminal-yellow">{item.ticker}</span>
            </div>
            {item.status === 'success' ? (
              <span className="flex items-center text-emerald-400 font-semibold text-[10px]">
                <CheckCircle2 className="w-3 h-3 mr-0.5" /> UPDATED
              </span>
            ) : (
              <span className="flex items-center text-red-400 font-semibold text-[10px]">
                <AlertCircle className="w-3 h-3 mr-0.5" /> FAILED
              </span>
            )}
          </div>
        ))}
    </div>
  );
};

export const AIChatPanel: React.FC = () => {
  const { chatHistory, isLoadingChat, sendChatMessage } = useTerminalStore();
  const [inputPrompt, setInputPrompt] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isLoadingChat]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isLoadingChat) return;

    const message = inputPrompt;
    setInputPrompt('');
    await sendChatMessage(message);
  };

  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg flex flex-col h-full overflow-hidden">
      {/* Sidebar Header */}
      <div className="p-3 border-b border-terminal-border bg-terminal-card/90 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-terminal-purple" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-white">
            FinAlly AI Copilot
          </h2>
        </div>
        <span className="text-[10px] font-mono px-1.5 py-0.5 bg-terminal-purple/20 text-purple-300 rounded border border-terminal-purple/40">
          GPT-OSS 120B
        </span>
      </div>

      {/* Message History */}
      <div className="flex-1 p-3 overflow-y-auto space-y-3">
        {chatHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-terminal-muted p-4">
            <Bot className="w-8 h-8 mb-2 text-terminal-purple/60 animate-bounce" />
            <p className="text-xs font-mono">
              Ask me to trade stocks, manage watchlists, or analyze portfolio risk.
            </p>
            <p className="text-[10px] text-terminal-muted/70 mt-1 font-mono">
              Try: &quot;Buy 5 shares of AAPL and add NVDA to watchlist&quot;
            </p>
          </div>
        ) : (
          chatHistory.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id || Math.random().toString()}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div className="flex items-center space-x-1 mb-1 text-[10px] text-terminal-muted font-mono">
                  {isUser ? (
                    <>
                      <span>Trader</span>
                      <User className="w-3 h-3 text-terminal-blue" />
                    </>
                  ) : (
                    <>
                      <Bot className="w-3 h-3 text-terminal-purple" />
                      <span>FinAlly AI</span>
                    </>
                  )}
                </div>

                <div
                  className={`p-2.5 rounded-lg text-xs font-mono max-w-[90%] leading-relaxed ${
                    isUser
                      ? 'bg-terminal-blue/20 border border-terminal-blue/40 text-white rounded-br-none'
                      : 'bg-terminal-bg border border-terminal-border text-gray-200 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  <ActionCards actions={msg.actions} />
                </div>
              </div>
            );
          })
        )}

        {isLoadingChat && (
          <div className="flex items-center space-x-2 text-terminal-purple text-xs font-mono p-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>FinAlly Copilot analyzing prompt...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Submission Bar */}
      <form onSubmit={handleSubmit} className="p-2 border-t border-terminal-border bg-terminal-card">
        <div className="flex items-center space-x-1.5">
          <input
            type="text"
            placeholder="Type prompt / trading command..."
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={isLoadingChat}
            className="flex-1 px-3 py-1.5 text-xs font-mono bg-terminal-bg border border-terminal-border rounded text-white focus:outline-none focus:border-terminal-purple"
          />
          <button
            type="submit"
            disabled={isLoadingChat || !inputPrompt.trim()}
            className="p-1.5 bg-terminal-purple hover:bg-purple-600 text-white rounded transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
