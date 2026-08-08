# FinAlly — AI Trading Workstation

## What This Is

FinAlly (Finance Ally) is a visually stunning AI-powered trading workstation that streams live market data, lets users trade a simulated portfolio, and integrates an LLM chat assistant that can analyze positions and execute trades on the user's behalf. It looks and feels like a modern Bloomberg terminal with an AI copilot.

## Core Value

Provide a high-performance, dark-themed trading workstation with real-time SSE market data streaming, instant simulated portfolio execution, and a zero-friction AI copilot that executes structured trades and watchlist updates seamlessly.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **MKT-01**: Live market data engine with geometric Brownian motion (GBM) simulation and optional Massive API support
- [ ] **MKT-02**: Server-Sent Events (SSE) streaming endpoint (`/api/stream/prices`) for real-time price updates (~500ms)
- [ ] **DB-01**: SQLite schema with lazy auto-initialization and default seed data (cash: $10,000, 10 default tickers)
- [ ] **PORT-01**: Portfolio tracking (cash balance, positions, unrealized P&L, portfolio weight) and market order trade execution (`/api/portfolio/trade`)
- [ ] **PORT-02**: Portfolio snapshot tracking over time (`/api/portfolio/history`) recorded every 30s and after trades
- [ ] **WATCH-01**: Watchlist management (`/api/watchlist`) supporting CRUD operations for tickers
- [ ] **AI-01**: LiteLLM/OpenRouter Cerebras integration (`openrouter/openai/gpt-oss-120b`) with structured JSON outputs for trade and watchlist execution
- [ ] **AI-02**: LLM mock mode (`LLM_MOCK=true`) for deterministic offline development and testing
- [ ] **UI-01**: Dark Bloomberg-style workstation layout with header status, live price grid, sparkline mini-charts, detail chart, portfolio treemap, positions table, trade bar, and AI chat panel
- [ ] **UI-02**: Price flash CSS highlight animations (green uptick, red downtick) with 500ms fade
- [ ] **DOCK-01**: Single-container Docker build with multi-stage Node export and FastAPI Python runtime serving static files on port 8000
- [ ] **DOCK-02**: Cross-platform startup and shutdown scripts (`scripts/start_mac.sh`, `scripts/stop_mac.sh`, `scripts/start_windows.ps1`, `scripts/stop_windows.ps1`)
- [ ] **TEST-01**: Pytest unit tests for backend logic, React testing library tests for UI, and Playwright E2E test suite in `test/`

### Out of Scope

- Limit orders, stop losses, margin trading, and order book matching engine — market orders only for simplicity
- Multi-user authentication and login — single-user mode default `user_id="default"`
- WebSocket bidirectional protocol — SSE is simpler and sufficient for one-way price streaming
- External database server requirement — SQLite file in volume mount is zero-config and persistent

## Context

- Tech stack: Frontend: Next.js (TypeScript, Tailwind CSS, static export); Backend: FastAPI (Python 3.12, `uv` package manager); Database: SQLite (`db/finally.db`); AI: LiteLLM via OpenRouter (`openrouter/openai/gpt-oss-120b` via Cerebras) with structured JSON output schema.
- Environment variables: `OPENROUTER_API_KEY`, `MASSIVE_API_KEY`, `LLM_MOCK`.
- Single container deployment serving static frontend files via FastAPI on port 8000.

## Constraints

- **Architecture**: Single Docker container listening on port 8000 (`output: 'export'` served by FastAPI)
- **Database**: SQLite file at `db/finally.db` volume-mounted into container
- **Package Management**: `uv` for Python backend, `npm` for Next.js frontend
- **Color Palette**: Dark theme background `#0d1117` / `#1a1a2e`, Accent Yellow `#ecad0a`, Primary Blue `#209dd7`, Secondary Purple `#753991`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SSE streaming over WebSockets | One-way server push is sufficient for market ticks; lower complexity and built-in browser retry | — Pending |
| Static Next.js export with FastAPI | Eliminates CORS issues, single container deployment on port 8000 | — Pending |
| Structured Output JSON for AI | Enables instant agentic trade execution and watchlist management from natural language chat | — Pending |
| Market orders only | Eliminates complex order book matching, partial fills, and limit state machines | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-08 after project initialization*
