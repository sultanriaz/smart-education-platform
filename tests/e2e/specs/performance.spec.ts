import { expect, test } from "@playwright/test";

import { login, type Role } from "../helpers/auth";

function p95(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil(sorted.length * 0.95) - 1)];
}

for (const role of ["student", "teacher", "admin"] as Role[]) {
  test(`${role} primary workspace navigation stays inside 3s smoke budget`, async ({
    page
  }) => {
    await login(page, role);

    const samples: number[] = [];
    for (let i = 0; i < 5; i += 1) {
      const started = performance.now();
      await page.goto(`/app/${role}`, { waitUntil: "networkidle" });
      samples.push(performance.now() - started);
      await expect(page.locator("main")).toBeVisible();
    }

    expect(p95(samples)).toBeLessThanOrEqual(3000);
  });
}
