import { expect, test } from "@playwright/test";

import { login } from "../helpers/auth";

test("anonymous user is redirected from protected application area", async ({ page }) => {
  await page.goto("/app/student");
  await expect(page).toHaveURL(/\/login/);
});

for (const role of ["student", "teacher", "admin"] as const) {
  test(`${role} can sign in to its own workspace`, async ({ page }) => {
    await login(page, role);
    await expect(page.locator("main")).toBeVisible();
  });
}

test("forgot-password response remains enumeration resistant in UI", async ({ page }) => {
  await page.goto("/forgot-password");
  await page.getByLabel("Email").fill("definitely-not-a-real-user@example.edu");
  await page.getByRole("button", { name: /send reset instructions/i }).click();
  await expect(
    page.getByText(/if the account is eligible/i)
  ).toBeVisible();
});
