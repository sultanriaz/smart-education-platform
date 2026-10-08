import { expect, type Page } from "@playwright/test";

export type Role = "student" | "teacher" | "admin";

export function credentials(role: Role) {
  const prefix = `SMARTEDU_E2E_${role.toUpperCase()}`;
  const email = process.env[`${prefix}_EMAIL`];
  const password = process.env[`${prefix}_PASSWORD`];

  if (!email || !password) {
    throw new Error(
      `${prefix}_EMAIL and ${prefix}_PASSWORD are required for E2E tests`
    );
  }
  return { email, password };
}

export async function login(page: Page, role: Role) {
  const { email, password } = credentials(role);
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  // Exercise the real login route within its per-IP security rate limit.
  const pacing = Number(process.env.SMARTEDU_E2E_LOGIN_PACING_MS ?? 0);
  if (pacing > 0) await new Promise(resolve => setTimeout(resolve, pacing));
  await page.getByRole("button", { name: /sign in/i }).click();

  await expect(page).toHaveURL(new RegExp(`/app/${role}(?:/|$|[?])`));
}

export async function logout(page: Page) {
  const button = page.getByRole("button", { name: /log out|sign out/i });
  if (await button.count()) {
    await button.first().click();
    await expect(page).toHaveURL(/\/login/);
  }
}
