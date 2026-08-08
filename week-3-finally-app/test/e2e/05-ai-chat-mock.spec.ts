import { test, expect } from '@playwright/test';
import { FinAllyPage } from './helpers';

test.describe('Scenario 5: AI Chat Interaction (Mock LLM Mode)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should send message to AI chat and display mock LLM response', async ({ page }) => {
    const ally = new FinAllyPage(page);

    // Verify chat panel is visible
    await expect(ally.chatPanel).toBeVisible();

    const userMessage = 'Analyze my current portfolio balance and positions';

    // Type prompt and click send
    await ally.chatInput.fill(userMessage);
    await ally.chatInput.press('Enter');

    // Verify user message appears in chat history
    await expect(page.locator(`text="${userMessage}"`)).toBeVisible();

    // Wait for mock LLM response to appear
    const assistantMessage = ally.chatMessages.last();
    await expect(assistantMessage).toBeVisible({ timeout: 10000 });
    const responseText = await assistantMessage.innerText();
    expect(responseText.length).toBeGreaterThan(0);
  });

  test('should render inline trade confirmation when AI assistant executes a trade', async ({ page }) => {
    const ally = new FinAllyPage(page);

    // Send a message asking the AI assistant to buy stock
    const tradePrompt = 'Buy 5 shares of MSFT for me';

    await ally.chatInput.fill(tradePrompt);
    await ally.chatInput.press('Enter');

    // Wait for response and inline trade confirmation
    await expect(ally.chatMessages.last()).toBeVisible({ timeout: 10000 });

    // Verify inline trade confirmation element or text
    const confirmation = ally.tradeConfirmations;
    await expect(confirmation.first()).toBeVisible({ timeout: 5000 });
  });
});
