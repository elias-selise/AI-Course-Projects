import { Page, Locator } from '@playwright/test';

/**
 * Page object helpers for FinAlly E2E tests.
 * Locators support both data-testid attributes and fallback standard UI patterns.
 */
export class FinAllyPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Header & Status
  get cashBalance(): Locator {
    return this.page.getByTestId('cash-balance');
  }

  get portfolioValue(): Locator {
    return this.page.getByTestId('portfolio-value');
  }

  get connectionStatus(): Locator {
    return this.page.getByTestId('connection-status');
  }

  // Watchlist
  get watchlistPanel(): Locator {
    return this.page.getByTestId('watchlist-panel');
  }

  get addTickerInput(): Locator {
    return this.page.getByTestId('add-ticker-input');
  }

  get addTickerButton(): Locator {
    return this.page.getByTestId('add-ticker-button');
  }

  getWatchlistRow(ticker: string): Locator {
    return this.page.getByTestId(`watchlist-item-${ticker}`);
  }

  getRemoveTickerButton(ticker: string): Locator {
    return this.page.getByTestId(`remove-ticker-${ticker}`);
  }

  // Trade Execution
  get tradeTickerInput(): Locator {
    return this.page.getByTestId('trade-ticker-input');
  }

  get tradeQuantityInput(): Locator {
    return this.page.getByTestId('trade-quantity-input');
  }

  get buyButton(): Locator {
    return this.page.getByTestId('buy-button');
  }

  get sellButton(): Locator {
    return this.page.getByTestId('sell-button');
  }

  get executeTradeButton(): Locator {
    return this.page.getByTestId('execute-trade-button');
  }

  // Positions Table
  get positionsTable(): Locator {
    return this.page.getByTestId('positions-table');
  }

  getPositionRow(ticker: string): Locator {
    return this.page.getByTestId(`position-row-${ticker}`);
  }

  // Visualizations
  get heatmapContainer(): Locator {
    return this.page.getByTestId('portfolio-heatmap');
  }

  get pnlChartContainer(): Locator {
    return this.page.getByTestId('pnl-chart');
  }

  // AI Chat
  get chatPanel(): Locator {
    return this.page.getByTestId('ai-chat-panel');
  }

  get chatInput(): Locator {
    return this.page.getByTestId('chat-input');
  }

  get chatSendButton(): Locator {
    return this.page.getByTestId('chat-send-button');
  }

  get chatMessages(): Locator {
    return this.page.getByTestId('chat-message');
  }

  get tradeConfirmations(): Locator {
    return this.page.getByTestId('trade-confirmation');
  }

  /**
   * Helper to parse numerical currency from string, e.g. "$10,000.00" -> 10000.00
   */
  parseCurrency(text: string): number {
    const cleaned = text.replace(/[^0-9.-]/g, '');
    return parseFloat(cleaned);
  }
}
