import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test.describe("Wave 17: Institutional Finance and Payroll Interfaces", () => {
  test("student can access fee portal and view tuition invoices", async ({ page }) => {
    await login(page, "student");
    await page.goto("/app/student/finance");

    // Verify page header and primary containers
    await expect(page.locator("h1")).toContainText(/Fees|Invoices|Finance/i);
    await expect(page.locator("main")).toBeVisible();

    // Verify key financial sections (Account Summary, Invoices, Payment history)
    const pageText = await page.textContent("main");
    expect(pageText).toMatch(/Tuition|Balance|Invoice|PKR|Account|Fee/i);
  });

  test("teacher can view payslips and compensation breakdown", async ({ page }) => {
    await login(page, "teacher");
    await page.goto("/app/teacher/payroll");

    // Verify header
    await expect(page.locator("h1")).toContainText(/Compensation|Payslips|Payroll/i);
    await expect(page.locator("main")).toBeVisible();

    // Verify payslip table or earnings summary
    const pageText = await page.textContent("main");
    expect(pageText).toMatch(/Salary|Allowance|Deduction|Net|PKR|Payslip/i);
  });

  test("admin can inspect finance general ledger, fee structures, and refunds", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/app/admin/finance");

    // Verify header
    await expect(page.locator("h1")).toContainText(/Finance|Fees/i);
    await expect(page.locator("main")).toBeVisible();

    // Verify financial management tabs
    await expect(page.getByRole("button", { name: "Overview" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Fee Structures & Scholarships" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Bulk Billing & Invoices" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Refunds/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "Double-Entry GL & Trial Balance" })).toBeVisible();

    // Switch to Double-Entry GL & Trial Balance tab
    await page.getByRole("button", { name: "Double-Entry GL & Trial Balance" }).click();
    const ledgerText = await page.textContent("main");
    expect(ledgerText).toMatch(/Debit|Credit|Balance|Trial Balance|Accounts Receivable|Tuition Revenue/i);
  });

  test("admin can manage payroll runs, maker-checker approval queue, and simulated disbursements", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/app/admin/payroll");

    // Verify header
    await expect(page.locator("h1")).toContainText(/Institutional Payroll|Disbursements/i);
    await expect(page.locator("main")).toBeVisible();

    // Verify payroll tabs
    await expect(page.getByRole("button", { name: "Overview" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Maker-Checker Approvals/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "Simulated Disbursements" })).toBeVisible();

    // Switch to Maker-Checker tab
    await page.getByRole("button", { name: /Maker-Checker Approvals/i }).click();
    await expect(page.getByRole("heading", { name: /Maker-Checker Payroll/i })).toBeVisible();
    await expect(page.getByLabel(/Simulate Payout Rail Failures/i)).toBeVisible();

    // Switch to Simulated Disbursements tab
    await page.getByRole("button", { name: "Simulated Disbursements" }).click();
    await expect(page.getByRole("heading", { name: /Simulated Bank Disbursements & Rails/i })).toBeVisible();
    const disbText = await page.textContent("main");
    expect(disbText).toMatch(/Batch Number|Total Amount|Employees|Failed|Reconciled|Status/i);
  });
});
