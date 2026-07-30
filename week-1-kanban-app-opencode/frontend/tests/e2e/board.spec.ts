import { test, expect } from '@playwright/test'

test.describe('Kanban Board', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('renders the board with 5 column headers', async ({ page }) => {
    const headers = page.locator('h2')
    await expect(headers).toHaveCount(5)
  })

  test('displays all 10 cards', async ({ page }) => {
    const cards = page.locator('h3')
    await expect(cards).toHaveCount(10)
  })

  test('adds a new card to a column', async ({ page }) => {
    await page.getByText('+ Add Card').first().click()
    await page.getByPlaceholder('Card title').fill('Test Card')
    await page.getByPlaceholder('Details (optional)').fill('Test details')
    await page.getByRole('button', { name: 'Add', exact: true }).last().click()
    await expect(page.getByText('Test Card')).toBeVisible()
  })

  test('deletes a card', async ({ page }) => {
    const firstCard = page.locator('h3').first()
    const title = await firstCard.textContent()
    await firstCard.locator('..').getByLabel('Delete card').click()
    await expect(page.getByText(title!)).toHaveCount(0)
  })

  test('renames a column', async ({ page }) => {
    await page.locator('h2').filter({ hasText: 'Backlog' }).click()
    const input = page.locator('input').first()
    await expect(input).toBeVisible()
    await input.fill('New Name')
    await input.press('Enter')
    await expect(page.locator('h2').filter({ hasText: 'New Name' })).toBeVisible()
  })

  test('edits a card title', async ({ page }) => {
    await page.locator('h3').first().click()
    const input = page.locator('input').first()
    await input.fill('Updated Title')
    await page.getByRole('button', { name: 'Save' }).click()
    await expect(page.getByText('Updated Title')).toBeVisible()
  })
})
