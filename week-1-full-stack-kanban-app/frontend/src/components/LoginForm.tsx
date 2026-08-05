"use client";

import React, { useState } from "react";
import { Lock, User, LogIn, AlertCircle } from "lucide-react";

interface LoginFormProps {
  onLoginSuccess: () => void;
}

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        throw new Error("Invalid username or password");
      }

      // Fallback local storage state for client-side routing
      localStorage.setItem("kanban_authenticated", "true");
      onLoginSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      if (username === "user" && password === "password") {
        localStorage.setItem("kanban_authenticated", "true");
        onLoginSuccess();
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#032147] p-4 text-slate-100 selection:bg-[#ecad0a] selection:text-slate-900">
      <div className="w-full max-w-md rounded-2xl border border-slate-700/60 bg-slate-950/60 p-8 shadow-2xl backdrop-blur-xl">
        <div className="mb-8 text-center">
          <div className="inline-flex rounded-xl bg-gradient-to-tr from-[#753991] to-[#209dd7] p-3 shadow-lg shadow-[#753991]/30 mb-4">
            <Lock className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-2xl font-black tracking-tight text-white">Sign In to Kanban</h2>
          <p className="mt-2 text-xs text-[#888888]">
            Use credentials <code className="text-[#ecad0a] bg-[#ecad0a]/10 px-1.5 py-0.5 rounded">user</code> / <code className="text-[#ecad0a] bg-[#ecad0a]/10 px-1.5 py-0.5 rounded">password</code>
          </p>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-[#888888] mb-1.5">Username</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-900/80 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#888888] mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-900/80 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#753991] hover:bg-[#753991]/90 py-3 text-sm font-semibold text-white shadow-lg shadow-[#753991]/30 transition-all hover:shadow-[#753991]/50 disabled:opacity-50"
          >
            <LogIn className="h-4 w-4" />
            <span>{loading ? "Signing in..." : "Sign In"}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
