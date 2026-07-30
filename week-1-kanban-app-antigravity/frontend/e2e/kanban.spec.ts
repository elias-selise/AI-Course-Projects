import { test, expect } from "@playwright/test";

test.describe("Kanban App Integration Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should render the single board with 5 default columns", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Project Kanban" })).toBeVisible();
    await expect(page.getByText("Backlog")).toBeVisible();
    await expect(page.getByText("To Do")).toBeVisible();
    await expect(page.getByText("In Progress")).toBeVisible();
    await expect(page.getByText("Review")).toBeVisible();
    await expect(page.getByText("Done")).toBeVisible();
  });

  test("should allow adding a new card to a column", async ({ page }) => {
    const backlogColumn = page.locator("div").filter({ hasText: /^Backlog/ }).first();
    await backlogColumn.getByRole("button", { name: "Add Card" }).click();

    await page.getByPlaceholder("Task title...").fill("E2E Playwright Task");
    await page.getByPlaceholder("Details (optional)...").fill("Testing automated addition");
    await page.getByRole("button", { name: "Add Card" }).click();

    await expect(page.getByText("E2E Playwright Task")).toBeVisible();
    await expect(page.getByText("Testing automated addition")).toBeVisible();
  });

  test("should allow renaming a column", async ({ page }) => {
    const renameBtn = page.getByRole("button", { name: "Rename column" }).first();
    await renameBtn.click();

    const input = page.locator("input[value='Backlog']");
    await input.fill("Ideas Pool");
    await page.getByRole("button", { name: "Save" }).click();

    await expect(page.getByText("Ideas Pool")).toBeVisible();
  });

  test("should allow deleting a card", async ({ page }) => {
    await expect(page.getByText("User Authentication")).toBeVisible();

    const deleteBtn = page.getByRole("button", { name: "Delete card User Authentication" });
    await deleteBtn.click({ force: true });

    await expect(page.getByText("User Authentication")).not.toBeVisible();
  });
});
