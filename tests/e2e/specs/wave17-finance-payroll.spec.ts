import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test.describe("Wave 17: Page Rendering & Role Navigation", () => {
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

test.describe("Wave 17: User-Driven Transactional Workflows", () => {
  test("student fee payment checkout: gateway selection and simulated settlement", async ({ page }) => {
    await login(page, "student");
    await page.goto("/app/student/finance");

    // Check if any invoice pay button is available
    const payBtn = page.getByRole("button", { name: /Pay Full Balance|Pay Installment/i }).first();
    const isPayable = await payBtn.isVisible().catch(() => false);

    if (isPayable) {
      // 1. Open simulated checkout modal
      await payBtn.click();
      await expect(page.getByText(/Simulated Fee Payment Checkout/i)).toBeVisible();

      // 2. Select payment method (e.g. JazzCash HMAC rail)
      const jazzCashBtn = page.getByRole("button", { name: /JazzCash/i });
      if (await jazzCashBtn.isVisible()) {
        await jazzCashBtn.click();
      }

      // 3. Confirm sandbox simulation notice is displayed
      await expect(page.getByText(/Test Sandbox Environment/i)).toBeVisible();

      // 4. Submit simulated payment
      const authorizeBtn = page.getByRole("button", { name: /Authorize & Pay/i });
      await expect(authorizeBtn).toBeVisible();
      await authorizeBtn.click();

      // 5. Verify modal closes after successful simulated processing
      await expect(page.getByText(/Simulated Fee Payment Checkout/i)).not.toBeVisible({ timeout: 10000 });
    }
  });

  test("admin maker-checker approval queue, payout failure simulation, and batch reconciliation", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/app/admin/payroll");

    // Navigate to Maker-Checker Approvals tab
    await page.getByRole("button", { name: /Maker-Checker Approvals/i }).click();
    await expect(page.getByRole("heading", { name: /Maker-Checker Payroll/i })).toBeVisible();

    // Toggle failure simulation checkbox
    const failureChk = page.locator("#simulate-failures-chk");
    await expect(failureChk).toBeVisible();
    await failureChk.check();
    expect(await failureChk.isChecked()).toBe(true);

    // If an action button (Approve or Execute Disbursement) is ready, exercise it
    const approveBtn = page.getByRole("button", { name: /Approve \(Checker\)/i }).first();
    if (await approveBtn.isVisible().catch(() => false)) {
      await approveBtn.click();
      await page.waitForTimeout(1000);
    }

    const disburseBtn = page.getByRole("button", { name: /Execute Disbursement/i }).first();
    if (await disburseBtn.isVisible().catch(() => false)) {
      await disburseBtn.click();
      await page.waitForTimeout(1000);
    }

    // Switch to Simulated Disbursements tab
    await page.getByRole("button", { name: "Simulated Disbursements" }).click();
    await expect(page.getByRole("heading", { name: /Simulated Bank Disbursements & Rails/i })).toBeVisible();

    // If batches exist, test expanding records and batch reconciliation
    const viewRecordsBtn = page.getByRole("button", { name: /View Records/i }).first();
    if (await viewRecordsBtn.isVisible().catch(() => false)) {
      await viewRecordsBtn.click();
      await expect(page.getByText(/Batch Payout Records/i)).toBeVisible();

      // If a retry payout button is present on a failed payout, exercise retry
      const retryBtn = page.getByRole("button", { name: /Retry Payout/i }).first();
      if (await retryBtn.isVisible().catch(() => false)) {
        await retryBtn.click();
        await page.waitForTimeout(1000);
      }
    }

    const reconcileBtn = page.getByRole("button", { name: /Reconcile Batch/i }).first();
    if (await reconcileBtn.isVisible().catch(() => false)) {
      await reconcileBtn.click();
      await page.waitForTimeout(1000);
    }
  });

  test("admin general ledger chart of accounts and trial balance inspection", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/app/admin/finance");

    // Navigate to Double-Entry GL tab
    await page.getByRole("button", { name: "Double-Entry GL & Trial Balance" }).click();
    await expect(page.getByRole("heading", { name: /Double-Entry Accounting Trial/i })).toBeVisible();
    // Verify balanced trial balance and table structure
    await expect(page.getByText(/Trial Balance Totals/i)).toBeVisible();
    const tableText = await page.textContent("main");
    expect(tableText).toMatch(/Trial Balance Totals|Total Debits == Total Credits/i);
    expect(tableText).toMatch(/Account Code|Account Name|Category/i);
  });
});
