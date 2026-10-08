import { expect, test } from "@playwright/test";

import { login, type Role } from "../helpers/auth";

const roles: Role[] = ["student", "teacher", "admin"];

for (const role of roles) {
  for (const other of roles.filter((value) => value !== role)) {
    test(`${role} cannot enter ${other} workspace`, async ({ page }) => {
      await login(page, role);
      await page.goto(`/app/${other}`);

      await expect(page).not.toHaveURL(new RegExp(`/app/${other}(?:/|$)`));
    });
  }
}
