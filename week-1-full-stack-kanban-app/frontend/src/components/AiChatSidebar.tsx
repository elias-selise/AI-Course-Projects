"use client";

import React, { useState, useRef, useEffect } from "react";
import { Sparkles, Send, Bot, User, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { Column } from "@/types/kanban";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface AiChatSidebarProps {
  onBoardUpdated: (newBoard: Column[]) => void;
}

export function AiChatSidebar({ onBoardUpdated }: AiChatSidebarProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I can manage your Kanban board. Try asking me to add, edit, or move cards!",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const history = messages
        .filter((m) => m.id !== "welcome")
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, history }),
      });

      const data = await res.json();
      if (res.ok && data.success) {
        const botMessage: Message = {
          id: `bot-${Date.now()}`,
          role: "assistant",
          content: data.reply || "Done!",
        };
        setMessages((prev) => [...prev, botMessage]);

        if (data.board && Array.isArray(data.board)) {
          onBoardUpdated(data.board);
        }
      } else {
        throw new Error(data.detail || "AI response failed");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to respond";
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: `Sorry, I encountered an issue: ${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`h-full border-l border-slate-700/60 bg-slate-950/90 backdrop-blur-xl transition-all duration-300 flex flex-col relative z-20 shrink-0 ${
        isOpen ? "w-80" : "w-12"
      }`}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -left-3.5 top-6 z-30 flex h-7 w-7 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-slate-300 hover:text-white shadow-lg hover:border-[#209dd7]/60 transition-colors"
        title={isOpen ? "Collapse AI Chat" : "Expand AI Chat"}
      >
        {isOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>

      {isOpen ? (
        <div className="flex h-full flex-col min-h-0 p-4">
          {/* Header */}
          <div className="shrink-0 flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-gradient-to-tr from-[#753991] to-[#209dd7] p-1.5 shadow-md">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <h3 className="font-bold text-white text-sm tracking-wide">AI Assistant</h3>
            </div>
            <span className="text-[10px] font-medium text-[#ecad0a] bg-[#ecad0a]/10 px-2 py-0.5 rounded-full border border-[#ecad0a]/30">
              GPT OSS 120B
            </span>
          </div>

          {/* Messages List - Scrollable within chat window only */}
          <div className="flex-1 overflow-y-auto min-h-0 py-3 space-y-3 pr-1 text-xs scrollbar-thin">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="h-6 w-6 shrink-0 rounded-full bg-[#209dd7]/20 border border-[#209dd7]/40 flex items-center justify-center text-[#209dd7]">
                    <Bot className="h-3.5 w-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[82%] rounded-xl p-3 leading-relaxed ${
                    msg.role === "user"
                      ? "bg-[#753991] text-white shadow-md shadow-[#753991]/20"
                      : "bg-slate-900/90 border border-slate-800 text-slate-200"
                  }`}
                >
                  {msg.content}
                </div>
                {msg.role === "user" && (
                  <div className="h-6 w-6 shrink-0 rounded-full bg-[#753991]/30 border border-[#753991]/50 flex items-center justify-center text-[#753991]">
                    <User className="h-3.5 w-3.5" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-2 items-center text-slate-400 text-xs py-1">
                <Loader2 className="h-4 w-4 animate-spin text-[#209dd7]" />
                <span>AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Action Prompt Suggestions */}
          <div className="shrink-0 py-2 border-t border-slate-800/80 space-y-1.5">
            <p className="text-[10px] font-semibold text-[#888888]">Quick Actions</p>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => handleSend("Add a card titled Write Unit Tests to To Do column")}
                className="rounded-lg border border-slate-800 bg-slate-900/60 px-2 py-1 text-[10px] text-slate-300 hover:border-[#209dd7]/50 hover:text-[#209dd7] transition-colors"
              >
                + Add Card
              </button>
              <button
                onClick={() => handleSend("Move Project Setup card to Done column")}
                className="rounded-lg border border-slate-800 bg-slate-900/60 px-2 py-1 text-[10px] text-slate-300 hover:border-[#ecad0a]/50 hover:text-[#ecad0a] transition-colors"
              >
                → Move Card
              </button>
            </div>
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="shrink-0 flex items-center gap-2 pt-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI to modify cards..."
              disabled={loading}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-900/90 px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7]"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-[#753991] p-2 text-white hover:bg-[#753991]/90 disabled:opacity-50 transition-all shadow-md shadow-[#753991]/30"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      ) : (
        <div className="flex flex-col items-center py-6 gap-4">
          <button
            onClick={() => setIsOpen(true)}
            className="rounded-lg bg-gradient-to-tr from-[#753991] to-[#209dd7] p-2 shadow-md hover:scale-105 transition-transform"
            title="Open AI Assistant"
          >
            <Sparkles className="h-5 w-5 text-white" />
          </button>
        </div>
      )}
    </div>
  );
}
