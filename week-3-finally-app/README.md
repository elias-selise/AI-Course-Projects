# FinAlly — AI Trading Workstation

FinAlly (Finance Ally) is a visually stunning AI-powered trading workstation that streams live market data, lets users trade a simulated portfolio, and integrates an LLM chat assistant that can analyze positions and execute trades on the user's behalf. It looks and feels like a modern Bloomberg terminal with an AI copilot.

This is the capstone project for an agentic AI coding course, built entirely by Coding Agents demonstrating how orchestrated AI agents can produce a production-quality full-stack application.

## Project Overview

- **Single Container**: Runs everything seamlessly via a single Docker command (FastAPI backend + Next.js frontend).
- **Frontend**: Next.js with TypeScript, built as a static export, and designed with a dark, data-dense Bloomberg-like aesthetic.
- **Backend**: FastAPI (Python), managed with `uv`.
- **Database**: SQLite (zero-config, volume-mounted for persistence).
- **Real-time Data**: Server-Sent Events (SSE) stream prices directly to the browser.
- **Market Data**: Built-in simulator by default, with optional real market data via Massive API (Polygon.io).
- **AI Integration**: Chat panel powered by OpenRouter (Cerebras for fast inference), capable of natural language trade execution.

## Getting Started

1. Clone the repository.
2. Ensure you have Docker installed.
3. Configure your `.env` file with an `OPENROUTER_API_KEY`.
4. Run the appropriate start script for your OS from the `scripts/` directory.
5. Open `http://localhost:8000` in your browser.

All comprehensive project documentation and planning documents can be found in the `planning/` directory.