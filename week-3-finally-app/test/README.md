# FinAlly E2E Integration Test Suite

This directory contains the Playwright End-to-End (E2E) integration test suite and Docker testing infrastructure for the **FinAlly AI Trading Workstation**.

## Test Scenarios

The suite covers 6 primary E2E scenarios:

1. **`01-launch-watchlist-balance.spec.ts`**: Launch app, verify $10,000 initial cash balance, connection status dot, default 10 tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX), and price streaming.
2. **`02-watchlist-crud.spec.ts`**: Watchlist CRUD (Add ticker `PYPL`, remove ticker `NFLX`).
3. **`03-trade-execution.spec.ts`**: Manual trade execution (Buy stock, verify position & cash reduction; Sell stock, verify position update & cash increase).
4. **`04-portfolio-visualization.spec.ts`**: Portfolio visualization (Treemap heatmap component rendering positions by weight/P&L, and P&L line chart for historical snapshots).
5. **`05-ai-chat-mock.spec.ts`**: AI Chat interaction with `LLM_MOCK=true` (Send chat message, verify mock LLM response, verify inline trade confirmation).
6. **`06-sse-resilience.spec.ts`**: SSE resilience and price update UI behavior (Active status indicator, continuous stream stability, and price flash UI feedback).

---

## Data TestID Conventions (Frontend Guidelines)

To ensure resilient and maintainable tests, components should include `data-testid` attributes matching this spec:

| UI Element | `data-testid` Attribute |
|---|---|
| Cash Balance | `data-testid="cash-balance"` |
| Portfolio Total Value | `data-testid="portfolio-value"` |
| Connection Status Dot | `data-testid="connection-status"` |
| Watchlist Panel / Grid | `data-testid="watchlist-panel"` |
| Watchlist Row / Card | `data-testid="watchlist-item-[TICKER]"` (e.g. `watchlist-item-AAPL`) |
| Add Ticker Input | `data-testid="add-ticker-input"` |
| Add Ticker Button | `data-testid="add-ticker-button"` |
| Remove Ticker Button | `data-testid="remove-ticker-[TICKER]"` |
| Trade Input Ticker | `data-testid="trade-ticker-input"` |
| Trade Input Quantity | `data-testid="trade-quantity-input"` |
| Buy Button | `data-testid="buy-button"` |
| Sell Button | `data-testid="sell-button"` |
| Positions Table | `data-testid="positions-table"` |
| Position Row | `data-testid="position-row-[TICKER]"` |
| Treemap Heatmap Container | `data-testid="portfolio-heatmap"` |
| P&L Chart Container | `data-testid="pnl-chart"` |
| AI Chat Panel | `data-testid="ai-chat-panel"` |
| Chat Input Field | `data-testid="chat-input"` |
| Chat Send Button | `data-testid="chat-send-button"` |
| Chat Message Bubble | `data-testid="chat-message"` |
| Inline Trade Confirmation | `data-testid="trade-confirmation"` |

---

## Running Tests

### Option 1: Docker Compose (Recommended for CI / Full Stack E2E)

Launch the application container alongside the Playwright test runner container with `LLM_MOCK=true`:

```bash
docker compose -f test/docker-compose.test.yml up --build --exit-code-from test-runner
```

### Option 2: Local Playwright Test Run

Ensure the backend/app is running on `http://localhost:8000` with `LLM_MOCK=true`.

```bash
cd test
npm install
npx playwright test
```

### Interactive UI / Debug Mode

```bash
cd test
npm run test:ui
# or
npm run test:debug
```

---

## Test Environment Variables

- `BASE_URL`: URL of the app under test (default: `http://localhost:8000`, set to `http://app:8000` inside Docker compose).
- `LLM_MOCK`: Always set to `true` during test runs for fast, deterministic LLM chat verification.
