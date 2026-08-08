# Requirements: FinAlly — AI Trading Workstation

**Defined:** 2026-08-08
**Core Value:** Provide a high-performance, dark-themed trading workstation with real-time SSE market data streaming, instant simulated portfolio execution, and a zero-friction AI copilot that executes structured trades and watchlist updates seamlessly.

## v1 Requirements

### Backend & Database

- [ ] **BACK-01**: FastAPI project setup with `uv` dependency management (`pyproject.toml`) and `/api/health` endpoint
- [ ] **DB-01**: SQLite lazy schema auto-initialization at `db/finally.db` with tables (`users_profile`, `watchlist`, `positions`, `trades`, `portfolio_snapshots`, `chat_messages`)
- [ ] **DB-02**: Seed database on initial startup ($10,000 cash balance, 10 default tickers: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX)

### Market Data Engine

- [ ] **MKT-01**: Abstract market data interface supporting both in-process Simulator (GBM model, 500ms ticks, correlated moves) and optional Massive API (Polygon.io REST polling)
- [ ] **MKT-02**: In-memory price cache storing latest price, previous price, and timestamp for all tickers
- [ ] **MKT-03**: SSE streaming endpoint `/api/stream/prices` pushing formatted JSON price ticks to connected clients

### Portfolio & Trading

- [ ] **PORT-01**: REST endpoint `GET /api/portfolio` returning positions, cash balance, total portfolio value, and unrealized P&L
- [ ] **PORT-02**: REST endpoint `POST /api/portfolio/trade` executing instant market orders (`buy`/`sell`), updating cash balance and position average cost
- [ ] **PORT-03**: Background task and post-trade trigger recording snapshots to `portfolio_snapshots` every 30s (`GET /api/portfolio/history`)
- [ ] **WATCH-01**: REST endpoints `GET /api/watchlist`, `POST /api/watchlist`, and `DELETE /api/watchlist/{ticker}`

### AI Assistant & LLM Integration

- [ ] **AI-01**: REST endpoint `POST /api/chat` loading portfolio context, recent chat history, and dispatching to OpenRouter via LiteLLM (`openrouter/openai/gpt-oss-120b` via Cerebras)
- [ ] **AI-02**: Structured output JSON parser for LLM responses (`message`, `trades`, `watchlist_changes`) with auto-execution of requested actions
- [ ] **AI-03**: `LLM_MOCK=true` mode returning deterministic JSON chat responses without external API calls

### Frontend Workstation UI

- [ ] **UI-01**: Next.js TypeScript project styled with Tailwind CSS in dark theme (`#0d1117` / `#1a1a2e`, yellow `#ecad0a`, blue `#209dd7`, purple `#753991`) with static export configuration (`output: 'export'`)
- [ ] **UI-02**: Terminal Header displaying total portfolio value, live SSE connection status indicator (green/yellow/red dot), and available cash balance
- [ ] **UI-03**: Watchlist Grid displaying live prices with green/red flash animations (500ms fade), % change, sparkline mini-charts, and ticker selection
- [ ] **UI-04**: Interactive Main Chart displaying selected ticker price history over time
- [ ] **UI-05**: Portfolio Heatmap (Treemap) visualizing position weights and P&L color coding (green profit / red loss)
- [ ] **UI-06**: Portfolio P&L Line Chart displaying total value history over time
- [ ] **UI-07**: Positions Table displaying ticker, quantity, avg cost, current price, unrealized P&L, and % change
- [ ] **UI-08**: Order Entry Trade Bar for instant market buy/sell order submission
- [ ] **UI-09**: AI Chat Panel sidebar with message history, loading states, and inline trade/watchlist action confirmation cards

### Deployment & Tooling

- [ ] **DOCK-01**: Multi-stage `Dockerfile` (Node static build + Python FastAPI runtime serving static export on port 8000)
- [ ] **SCR-01**: Shell & PowerShell start/stop scripts (`scripts/start_mac.sh`, `scripts/stop_mac.sh`, `scripts/start_windows.ps1`, `scripts/stop_windows.ps1`)
- [ ] **TEST-01**: Pytest suite for backend routes & market simulator, React component tests, and Playwright E2E test suite in `test/`

## Out of Scope

| Feature | Reason |
|---------|--------|
| Limit & Stop Orders | Adds complex order book state machine; market orders provide fluid demo experience |
| Authentication & Signup | Single-user local trading workstation defaults to user_id="default" |
| WebSockets | SSE handles one-way server-to-client price ticks with lower overhead |
| Postgres / External DB | SQLite file in Docker volume mount provides zero-config persistence |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | Phase 1 | Pending |
| DB-01 | Phase 1 | Pending |
| DB-02 | Phase 1 | Pending |
| MKT-01 | Phase 1 | Pending |
| MKT-02 | Phase 1 | Pending |
| MKT-03 | Phase 1 | Pending |
| PORT-01 | Phase 2 | Pending |
| PORT-02 | Phase 2 | Pending |
| PORT-03 | Phase 2 | Pending |
| WATCH-01 | Phase 2 | Pending |
| AI-01 | Phase 3 | Pending |
| AI-02 | Phase 3 | Pending |
| AI-03 | Phase 3 | Pending |
| UI-01 | Phase 4 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| UI-04 | Phase 4 | Pending |
| UI-05 | Phase 4 | Pending |
| UI-06 | Phase 4 | Pending |
| UI-07 | Phase 4 | Pending |
| UI-08 | Phase 4 | Pending |
| UI-09 | Phase 4 | Pending |
| DOCK-01 | Phase 5 | Pending |
| SCR-01 | Phase 5 | Pending |
| TEST-01 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-08*
*Last updated: 2026-08-08 after initial definition*
