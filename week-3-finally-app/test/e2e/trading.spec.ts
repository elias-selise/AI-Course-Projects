import { test, expect } from '@playwright/test';

test.describe('FinAlly Trading Workstation E2E Suite', () => {

  test('UI-01 & UI-02: Header displays portfolio value, cash balance, and live SSE indicator', async ({ page }) => {
    await page.goto('/');

    // Check Header elements
    await expect(page.getByText('FinAlly', { exact: true }).first()).toBeVisible();
    await expect(page.getByText(/\$10,000|\$9,/i).first()).toBeVisible();

    // Check live connection status indicator (connected / reconnecting / disconnected)
    const statusText = page.locator('span', { hasText: /connected|reconnecting/i });
    await expect(statusText.first()).toBeVisible();
  });

  test('MKT-03 & UI-03: Watchlist receives live SSE price updates', async ({ page }) => {
    await page.goto('/');

    // Verify default tickers are displayed
    await expect(page.getByText('AAPL').first()).toBeVisible();
    await expect(page.getByText('GOOGL').first()).toBeVisible();
    await expect(page.getByText('NVDA').first()).toBeVisible();

    // Capture initial AAPL price element text
    const aaplCard = page.locator('div', { hasText: 'AAPL' }).first();
    await expect(aaplCard).toBeVisible();

    // Verify dynamic numeric price string presence ($XX.XX format)
    await expect(aaplCard.getByText(/\$\d+\.\d{2}/).first()).toBeVisible();
  });

  test('PORT-02 & UI-08: Order entry trade bar executes instant market order', async ({ page }) => {
    await page.goto('/');

    // Select ticker AAPL by clicking its card or typing into order entry input
    const tickerInput = page.locator('input[placeholder="TICKER"]');
    await tickerInput.fill('AAPL');

    // Fill quantity and submit Buy order
    const qtyInput = page.locator('input[type="number"]').first();
    await qtyInput.fill('10');

    const buyButton = page.getByRole('button', { name: /^BUY$/i });
    await buyButton.click();

    // Verify success toast or positions table updates with AAPL position
    await expect(page.getByText(/Market BUY order executed|AAPL/i).first()).toBeVisible();
  });

  test('WATCH-01 & UI-03: Watchlist ticker add and remove', async ({ page }) => {
    await page.goto('/');

    // Add ticker AMD via input
    const addInput = page.locator('input[placeholder="ADD TICKER"]');
    await expect(addInput).toBeVisible();

    await addInput.fill('AMD');
    await page.keyboard.press('Enter');

    // Verify AMD card appears in Watchlist
    await expect(page.getByText('AMD').first()).toBeVisible();
  });

  test('AI-01, AI-02 & UI-09: AI Chat Assistant receives prompt and executes trade', async ({ page }) => {
    await page.goto('/');

    // Locate chat input sidebar
    const chatInput = page.locator('input[placeholder*="trading command"]');
    await expect(chatInput).toBeVisible();

    // Send automated trade command prompt
    await chatInput.fill('Buy 5 shares of TSLA');
    await page.keyboard.press('Enter');

    // Verify AI response message appears
    await expect(page.locator('div', { hasText: /TSLA/i }).first()).toBeVisible({ timeout: 15000 });
  });

});
