import { test, expect } from '@playwright/test';
import { FinAllyPage } from './helpers';

test.describe('Scenario 2: Watchlist CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should add a new ticker to the watchlist', async ({ page }) => {
    const ally = new FinAllyPage(page);

    const newTicker = 'PYPL';
    const rowBefore = ally.getWatchlistRow(newTicker);
    await expect(rowBefore).not.toBeVisible();

    // Type ticker symbol into input field and submit
    await ally.addTickerInput.fill(newTicker);
    await ally.addTickerButton.click();

    // Verify ticker is added to the watchlist
    const rowAfter = ally.getWatchlistRow(newTicker);
    await expect(rowAfter).toBeVisible({ timeout: 5000 });
  });

  test('should remove a ticker from the watchlist', async ({ page }) => {
    const ally = new FinAllyPage(page);

    const targetTicker = 'TSLA';
    const targetRow = ally.getWatchlistRow(targetTicker);
    await expect(targetRow).toBeVisible({ timeout: 10000 });

    // Click remove button for the ticker
    const removeBtn = ally.getRemoveTickerButton(targetTicker);
    await removeBtn.click();

    // Verify ticker is removed from the watchlist
    await expect(targetRow).not.toBeVisible({ timeout: 5000 });
  });
});
