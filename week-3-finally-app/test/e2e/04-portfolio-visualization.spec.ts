import { test, expect } from '@playwright/test';
import { FinAllyPage } from './helpers';

test.describe('Scenario 4: Portfolio Visualization (Heatmap & P&L Chart)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should render the portfolio heatmap treemap visualization', async ({ page }) => {
    const ally = new FinAllyPage(page);

    // Buy a position to ensure portfolio holds assets
    await ally.tradeTickerInput.fill('NVDA');
    await ally.tradeQuantityInput.fill('5');
    await ally.buyButton.click();

    // Verify heatmap container is visible
    const heatmap = ally.heatmapContainer;
    await expect(heatmap).toBeVisible({ timeout: 10000 });

    // Verify canvas/svg or rect children inside heatmap
    const heatmapCanvasOrSvg = heatmap.locator('canvas, svg, div[class*="treemap"], div[class*="cell"], div[class*="tile"]');
    await expect(heatmapCanvasOrSvg.first()).toBeVisible({ timeout: 5000 });
  });

  test('should render the P&L line chart displaying historical portfolio snapshots', async ({ page }) => {
    const ally = new FinAllyPage(page);

    // Verify P&L chart container is visible
    const pnlChart = ally.pnlChartContainer;
    await expect(pnlChart).toBeVisible({ timeout: 10000 });

    // Verify chart rendering (canvas or svg elements)
    const chartContent = pnlChart.locator('canvas, svg, path, .recharts-surface, .tv-lightweight-charts');
    await expect(chartContent.first()).toBeVisible({ timeout: 5000 });
  });
});
