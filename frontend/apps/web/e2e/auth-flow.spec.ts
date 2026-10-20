import { test, expect } from "@playwright/test";

test.describe("auth shell", () => {
  test.skip(true, "Requires backend + Mailpit; run manually in local stack");

  test("register page renders", async ({ page }) => {
    await page.goto("/en/register");
    await expect(page.getByRole("heading")).toBeVisible();
  });
});
