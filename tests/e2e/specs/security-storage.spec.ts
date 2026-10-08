import { expect, test } from "@playwright/test";

import { login } from "../helpers/auth";

test("authenticated browser storage contains no auth tokens", async ({ page }) => {
  await login(page, "student");

  const storage = await page.evaluate(() => ({
    local: { ...window.localStorage },
    session: { ...window.sessionStorage }
  }));

  const serialized = JSON.stringify(storage).toLowerCase();
  expect(serialized).not.toContain("access_token");
  expect(serialized).not.toContain("refresh_token");
  expect(serialized).not.toContain("sep.access_token");
  expect(serialized).not.toContain("sep.refresh_token");
});
