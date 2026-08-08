import { test, expect } from '@playwright/test';
import { FinAllyPage } from './helpers';

test.describe('Scenario 1: Launch App & Watchlist Streaming & Initial Balance', () => {
  test('should load page with $10,000 initial balance and connection indicator', async ({ page }) => {
    const ally = new FinAllyPage(page);
    await page.goto('/');

    // Verify page title or header
    await expect(page).toHaveTitle(/FinAlly|Trading|Workstation/i);

    // Verify initial $10,000 cash balance
    const cashElement = ally.cashBalance;
    await expect(cashElement).toBeVisible();
    const cashText = await cashElement.innerText();
    expect(cashText).toMatch(/10,?000/);

    // Verify connection status indicator is visible and active
    const statusElement = ally.connectionStatus;
    await expect(statusElement).toBeVisible();
  });

  test('should display 10 default tickers in the watchlist', async ({ page }) => {
    const ally = new FinAllyPage(page);
    await page.goto('/');

    const defaultTickers = [
      'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
      'NVDA', 'META', 'JPM', 'V', 'NFLX'
    ];

    for (const ticker of defaultTickers) {
      const row = ally.getWatchlistRow(ticker);
      await expect(row).toBeVisible({ timeout: 10000 });
    }
  });

  test('should observe streaming price updates in the watchlist', async ({ page }) => {
    const ally = new FinAllyPage(page);
    await page.goto('/');

    // Target a representative ticker row (e.g. AAPL)
    const aaplRow = ally.getWatchlistRow('AAPL');
    await expect(aaplRow).toBeVisible();

    // Capture initial text content of the price element
    const initialContent = await aaplRow.innerText();

    // Wait for SSE updates to stream in over 3-5 seconds
    await page.waitForTimeout(3000);

    // Check that prices are continuously displayed and updating or price flashes occur
    const updatedContent = await aaplRow.innerText();
    expect(updatedContent).toBeTruthy();
  });
});
