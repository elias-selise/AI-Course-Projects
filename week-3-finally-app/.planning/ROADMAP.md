# Roadmap: FinAlly — AI Trading Workstation

## Milestones

- **[x] v1.0 MVP Core Trading Workstation & AI Copilot** — All 5 Phases Completed (2026-08-08)

## Phase Structure

- **[x] Phase 1: Backend Foundation, Database & Market Data Streaming Engine** (Completed 2026-08-08)
  - Setup FastAPI backend with `uv`
  - Implement SQLite database schema with auto-initialization & seed data
  - Build market data engine (GBM simulator + Massive API client + shared price cache)
  - Implement `/api/stream/prices` SSE endpoint and `/api/health`

- **[x] Phase 2: Portfolio Engine, Trading & Watchlist REST APIs** (Completed 2026-08-08)
  - Implement `/api/portfolio` (positions, cash balance, unrealized P&L)
  - Implement `/api/portfolio/trade` (market buy/sell execution)
  - Implement `/api/portfolio/history` (snapshot background task + trade trigger)
  - Implement `/api/watchlist` CRUD endpoints

- **[x] Phase 3: AI Copilot & Agentic Trade Execution** (Completed 2026-08-08)
  - Build OpenRouter / LiteLLM integration (`openrouter/openai/gpt-oss-120b` via Cerebras)
  - Implement structured JSON output parser and prompt builder with portfolio context
  - Build auto-execution module for AI-driven trades and watchlist changes
  - Implement `LLM_MOCK=true` mode and `/api/chat` endpoint

- **[x] Phase 4: Next.js Frontend Trading Terminal UI** (Completed 2026-08-08)
  - Setup Next.js TypeScript app with Tailwind CSS dark Bloomberg aesthetic (`output: 'export'`)
  - Implement SSE market data subscriber with price flash animations and sparklines
  - Build Watchlist Grid, Main Price Chart, Portfolio Heatmap Treemap, and P&L Line Chart
  - Build Positions Table, Order Entry Trade Bar, Header Status, and AI Chat Sidebar Panel

- **[x] Phase 5: Docker Containerization, Scripts & E2E Testing Suite** (Completed 2026-08-08)
  - Build multi-stage `Dockerfile` (Node static export build + Python FastAPI runtime on port 8000)
  - Create cross-platform launcher scripts (`start_mac.sh`, `stop_mac.sh`, `start_windows.ps1`, `stop_windows.ps1`)
  - Create Playwright E2E testing suite in `test/` with `docker-compose.test.yml`
  - Verify complete end-to-end functionality

---
*Roadmap defined: 2026-08-08*
