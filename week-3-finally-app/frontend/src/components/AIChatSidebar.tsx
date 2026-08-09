import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import { Bot, Send, Sparkles, Zap, Star, User, Loader2, ChevronRight, ChevronLeft } from 'lucide-react';

interface AIChatSidebarProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
}

const QUICK_PROMPTS = [
  "Analyze my portfolio risk & P&L",
  "Buy 5 shares of NVDA",
  "Sell 5 shares of TSLA",
  "Add AMD to my watchlist",
];

const AIChatSidebarComponent: React.FC<AIChatSidebarProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  const [input, setInput] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickPrompt = (prompt: string) => {
    if (isLoading) return;
    onSendMessage(prompt);
  };

  if (isCollapsed) {
    return (
      <div className="bg-panel border-l border-border w-12 flex flex-col items-center py-4 select-none">
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 text-accent-purple hover:text-white hover:bg-accent-purple/20 rounded transition-colors"
          title="Expand AI Assistant Panel"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="mt-8 text-accent-purple font-mono text-xs font-bold [writing-mode:vertical-rl] rotate-180 tracking-widest flex items-center gap-2">
          <Bot className="w-4 h-4 text-accent-purple" /> FINALLY AI COPILOT
        </div>
      </div>
    );
  }

  return (
    <aside data-testid="ai-chat-panel" className="bg-panel border-l border-border w-80 lg:w-96 flex flex-col h-full select-none">
      {/* Sidebar Header */}
      <div className="bg-panel-header px-3.5 py-2.5 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-accent-purple/20 border border-accent-purple/40 text-purple-300">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1">
              FINALLY AI COPILOT
              <Sparkles className="w-3 h-3 text-accent-yellow animate-pulse" />
            </h2>
            <span className="text-[9px] font-mono text-gray-400">Cerebras Fast Inference Powered</span>
          </div>
        </div>

        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1 text-gray-400 hover:text-white rounded hover:bg-gray-800 transition-colors"
          title="Collapse Panel"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Quick Prompts Carousel/Grid */}
      <div className="p-2 border-b border-border/60 bg-black/20 flex gap-1.5 overflow-x-auto no-scrollbar">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickPrompt(prompt)}
            disabled={isLoading}
            className="whitespace-nowrap px-2 py-1 rounded bg-gray-800/80 hover:bg-accent-purple/30 border border-border text-[10px] font-mono text-gray-300 hover:text-white transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Conversation Message List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 font-mono text-xs">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';

          return (
            <div
              key={msg.id}
              data-testid="chat-message"
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              {/* Role Header */}
              <div className="flex items-center gap-1.5 text-[10px] text-gray-400 mb-1">
                {isUser ? (
                  <>
                    <span>YOU</span>
                    <User className="w-3 h-3 text-accent-blue" />
                  </>
                ) : (
                  <>
                    <Bot className="w-3 h-3 text-accent-purple" />
                    <span className="text-purple-300 font-semibold">FINALLY AI</span>
                  </>
                )}
                <span className="text-[9px] opacity-60" suppressHydrationWarning>
                  {new Date(msg.timestamp || msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Message Content Bubble */}
              <div
                className={`p-3 rounded-lg max-w-[92%] leading-relaxed ${
                  isUser
                    ? 'bg-accent-blue/20 border border-accent-blue/40 text-blue-100 rounded-tr-none'
                    : 'bg-panel-header border border-border text-gray-200 rounded-tl-none shadow-sm'
                }`}
              >
                {msg.content}

                {/* Inline Trade Action Confirmation Badges */}
                {msg.actions?.trades && msg.actions.trades.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-border/80 space-y-1.5">
                    {msg.actions.trades.map((t, i) => (
                      <div
                        key={i}
                        data-testid="trade-confirmation"
                        className={`p-1.5 rounded border text-[10px] font-bold flex items-center gap-1.5 ${
                          t.side === 'buy'
                            ? 'bg-emerald-950/80 border-emerald-500/60 text-emerald-300'
                            : 'bg-rose-950/80 border-rose-500/60 text-rose-300'
                        }`}
                      >
                        <Zap className="w-3.5 h-3.5" />
                        <span>AUTO-EXECUTED: {t.side.toUpperCase()} {t.quantity} {t.ticker} {t.price ? `@ $${t.price.toFixed(2)}` : ''}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Inline Watchlist Action Badges */}
                {msg.actions?.watchlist_changes && msg.actions.watchlist_changes.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-border/80 space-y-1.5">
                    {msg.actions.watchlist_changes.map((w, i) => (
                      <div
                        key={i}
                        className="p-1.5 rounded border bg-amber-950/80 border-amber-500/60 text-amber-300 text-[10px] font-bold flex items-center gap-1.5"
                      >
                        <Star className="w-3.5 h-3.5 text-accent-yellow" />
                        <span>WATCHLIST MODIFIED: {w.action.toUpperCase()} {w.ticker}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex flex-col items-start font-mono">
            <div className="flex items-center gap-1.5 text-[10px] text-purple-300 mb-1">
              <Bot className="w-3 h-3 text-accent-purple" />
              <span>FINALLY AI IS THINKING...</span>
            </div>
            <div className="p-3 rounded-lg bg-panel-header border border-border text-purple-300 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-accent-purple" />
              <span className="text-xs">Analyzing market data & generating response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input Form */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-border bg-panel-header">
        <div className="flex items-center gap-2">
          <input
            type="text"
            data-testid="chat-input"
            placeholder="Ask AI to analyze or execute trades..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="flex-1 px-3 py-2 bg-black/60 border border-border rounded text-xs font-mono text-white placeholder-gray-500 focus:outline-none focus:border-accent-purple"
          />
          <button
            type="submit"
            data-testid="chat-send-button"
            disabled={isLoading || !input.trim()}
            className="p-2 rounded bg-accent-purple hover:bg-purple-600 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send Message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </aside>
  );
};

export const AIChatSidebar = React.memo(AIChatSidebarComponent);
