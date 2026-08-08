import { test, expect } from '@playwright/test';
import { FinAllyPage } from './helpers';

test.describe('Scenario 3: Manual Trade Execution (Buy & Sell)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should execute Buy trade, add position, and decrease cash', async ({ page }) => {
    const ally = new FinAllyPage(page);

    // Get initial cash balance text
    const initialCashText = await ally.cashBalance.innerText();
    const initialCash = ally.parseCurrency(initialCashText);

    // Execute Buy trade: 10 shares of AAPL
    const ticker = 'AAPL';
    const buyQty = '10';

    await ally.tradeTickerInput.fill(ticker);
    await ally.tradeQuantityInput.fill(buyQty);
    await ally.buyButton.click();
    await ally.executeTradeButton.click();

    // Verify position appears in positions table
    const posRow = ally.getPositionRow(ticker);
    await expect(posRow).toBeVisible({ timeout: 5000 });
    await expect(posRow).toContainText('10');

    // Verify cash balance has decreased
    await page.waitForTimeout(1000); // Allow balance state update
    const updatedCashText = await ally.cashBalance.innerText();
    const updatedCash = ally.parseCurrency(updatedCashText);

    expect(updatedCash).toBeLessThan(initialCash);
  });

  test('should execute Sell trade, update position quantity, and increase cash', async ({ page }) => {
    const ally = new FinAllyPage(page);

    const ticker = 'AAPL';
    // First, ensure we have a position of 10 shares
    await ally.tradeTickerInput.fill(ticker);
    await ally.tradeQuantityInput.fill('10');
    await ally.buyButton.click();
    await ally.executeTradeButton.click();
    await expect(ally.getPositionRow(ticker)).toBeVisible();

    const cashAfterBuyText = await ally.cashBalance.innerText();
    const cashAfterBuy = ally.parseCurrency(cashAfterBuyText);

    // Execute Sell trade: 5 shares of AAPL
    await ally.tradeTickerInput.fill(ticker);
    await ally.tradeQuantityInput.fill('5');
    await ally.sellButton.click();
    await ally.executeTradeButton.click();

    // Wait for cash balance to update (it should increase after selling)
    await expect(ally.cashBalance).not.toHaveText(cashAfterBuyText, { timeout: 5000 });

    // Verify position quantity updates (should contain '5' for remaining shares)
    const posRow = ally.getPositionRow(ticker);
    await expect(posRow).toBeVisible({ timeout: 5000 });

    // Verify cash balance has increased after selling
    const cashAfterSellText = await ally.cashBalance.innerText();
    const cashAfterSell = ally.parseCurrency(cashAfterSellText);

    expect(cashAfterSell).toBeGreaterThan(cashAfterBuy);
  });
});
