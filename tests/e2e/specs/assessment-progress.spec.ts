import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test("saved assessment resumes after reload and submits through the real API", async ({ page }) => {
  const assignmentId = process.env.SMARTEDU_E2E_ASSIGNMENT_ID;
  test.skip(!assignmentId, "Requires a disposable assigned demo assessment");
  await login(page, "student");
  await page.goto(`/app/student/assessments/${assignmentId}`);
  await page.getByRole("button", { name: /start attempt|resume attempt/i }).click();
  await page.getByLabel("Transactional outbox", { exact: true }).check();
  await page.getByRole("button", { name: "Save progress" }).click();
  await expect(page.getByText("Answers saved.", { exact: true })).toBeVisible();
  await page.reload();
  await page.getByRole("button", { name: "Resume attempt" }).click();
  await expect(page.getByLabel("Transactional outbox", { exact: true })).toBeChecked();
  await page.getByRole("button", { name: "Submit assessment" }).click();
  await expect(page).toHaveURL(/\/app\/student\/assessments$/);
  await expect(page.getByRole("cell", { name: "100.0%", exact: true }).first()).toBeVisible();
});
