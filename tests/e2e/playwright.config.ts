import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.SMARTEDU_FRONTEND_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "./specs",
  timeout: 45_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["list"],
    ["json", { outputFile: "../../artifacts/browser/e2e.json" }],
    ["html", { outputFolder: "playwright-report", open: "never" }]
  ],
  use: {
    baseURL,
    channel: process.env.SMARTEDU_BROWSER_CHANNEL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: process.env.SMARTEDU_E2E_VIDEO === "false" ? "off" : "retain-on-failure"
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  outputDir: "test-results"
});
