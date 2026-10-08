import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test("ten minutes of inactivity revokes the cookie session and clears the workspace", async ({ page }) => {
  await page.clock.install();
  await login(page, "student");
  await page.clock.fastForward(9 * 60 * 1000);
  await expect(page).toHaveURL(/\/app\/student/);
  await page.clock.fastForward(61 * 1000);
  await expect(page).toHaveURL(/\/login/);
  await page.reload();
  await expect(page).toHaveURL(/\/login/);
});
