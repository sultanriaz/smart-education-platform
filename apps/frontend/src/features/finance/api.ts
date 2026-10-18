import { apiRequest } from "../../lib/api-client";

export interface FeeStructure {
  id: string;
  name: string;
  academic_year: string;
  term: string;
  program: string;
  total_fee: number;
  currency: string;
  is_active: boolean;
  components: Array<{
    id: string;
    component_name: string;
    amount: number;
    is_tuition: boolean;
  }>;
}

export interface Scholarship {
  id: string;
  name: string;
  code: string;
  scholarship_type: "MERIT" | "NEED_BASED" | "SPECIAL";
  discount_percentage: number;
  max_discount_amount?: number;
  applies_to_tuition_only: boolean;
  is_active: boolean;
}

export interface StudentFinancialAccount {
  id: string;
  student_id: string;
  total_billed: number;
  total_paid: number;
  total_discounted: number;
  current_balance: number;
  currency: string;
}

export interface InvoiceInstallment {
  id: string;
  installment_number: number;
  amount_due: number;
  late_fee_amount: number;
  paid_amount: number;
  due_date: string;
  grace_period_end_date: string;
  status: "PENDING" | "PARTIAL" | "PAID" | "OVERDUE";
}

export interface Invoice {
  id: string;
  invoice_number: string;
  student_id: string;
  fee_structure_id: string;
  total_amount: number;
  discount_amount: number;
  payable_amount: number;
  paid_amount: number;
  balance_amount: number;
  status: "DRAFT" | "ISSUED" | "PARTIALLY_PAID" | "PAID" | "VOID" | "OVERDUE";
  due_date: string;
  created_at: string;
  line_items?: Array<{
    id: string;
    description: string;
    amount: number;
  }>;
  installments?: InvoiceInstallment[];
}

export interface PaymentIntent {
  intent_id: string;
  student_id: string;
  invoice_id: string;
  installment_id?: string;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
}

export interface Payment {
  id: string;
  payment_number: string;
  student_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  gateway_reference: string;
  status: string;
  created_at: string;
}

export interface RefundRequest {
  id: string;
  refund_number: string;
  payment_id: string;
  student_id: string;
  amount: number;
  reason: string;
  status: "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "COMPLETED";
  maker_id: string;
  checker_id?: string;
  created_at: string;
}

export interface ReconciliationBatch {
  id: string;
  batch_number: string;
  gateway: string;
  status: "PENDING" | "PROCESSING" | "MATCHED" | "DISCREPANCY" | "COMPLETED";
  total_records: number;
  matched_records: number;
  unmatched_records: number;
  total_amount: number;
  created_at: string;
}

export interface TrialBalanceAccount {
  account_code: string;
  account_name: string;
  account_type: string;
  debit_balance: number;
  credit_balance: number;
}

export interface TrialBalance {
  as_of_date: string;
  total_debits: number;
  total_credits: number;
  is_balanced: boolean;
  accounts: TrialBalanceAccount[];
}

export interface FinanceSummary {
  total_billed: number;
  total_collected: number;
  total_outstanding: number;
  total_refunded: number;
  active_invoices_count: number;
  collection_rate: number;
}

export interface StudentPortalOverview {
  account: StudentFinancialAccount;
  invoices: Invoice[];
  payments: Payment[];
  scholarships: Scholarship[];
}

// Finance API client calls
export const financeApi = {
  getSummary: () => apiRequest<FinanceSummary>("/api/v1/finance/reports/summary"),

  // Fee Structures
  getFeeStructures: () => apiRequest<FeeStructure[]>("/api/v1/finance/fee-structures"),
  createFeeStructure: (payload: {
    name: string;
    academic_year: string;
    term: string;
    program: string;
    components: Array<{ component_name: string; amount: number; is_tuition: boolean }>;
  }) =>
    apiRequest<FeeStructure>("/api/v1/finance/fee-structures", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Scholarships
  getScholarships: () => apiRequest<Scholarship[]>("/api/v1/finance/scholarships"),
  createScholarship: (payload: {
    name: string;
    code: string;
    scholarship_type: string;
    discount_percentage: number;
    max_discount_amount?: number;
    applies_to_tuition_only: boolean;
  }) =>
    apiRequest<Scholarship>("/api/v1/finance/scholarships", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  awardScholarship: (payload: { scholarship_id: string; student_id: string; academic_year: string; semester: string }) =>
    apiRequest("/api/v1/finance/scholarships/awards", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Invoices
  getInvoices: (params?: { student_id?: string; status?: string }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return apiRequest<Invoice[]>(`/api/v1/finance/invoices${query ? `?${query}` : ""}`);
  },
  getInvoiceDetails: (invoiceId: string) =>
    apiRequest<Invoice>(`/api/v1/finance/invoices/${invoiceId}`),
  previewBulkInvoices: (payload: { fee_structure_id: string; student_ids: string[]; num_installments?: number }) =>
    apiRequest<{ total_previewed: number; students: Array<{ student_id: string; total: number; payable: number }> }>(
      "/api/v1/finance/invoices/preview-bulk",
      {
        method: "POST",
        body: JSON.stringify(payload)
      }
    ),
  generateBulkInvoices: (payload: { fee_structure_id: string; student_ids: string[]; num_installments?: number }) =>
    apiRequest<{ total_created: number; invoice_ids: string[] }>("/api/v1/finance/invoices/generate-bulk", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Payments
  getPayments: (studentId?: string) => {
    const query = studentId ? `?student_id=${studentId}` : "";
    return apiRequest<Payment[]>(`/api/v1/finance/payments${query}`);
  },
  createPaymentIntent: (payload: {
    student_id: string;
    invoice_id: string;
    installment_id?: string;
    amount: number;
    payment_method: string;
  }) =>
    apiRequest<PaymentIntent>("/api/v1/finance/payments/intents", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  processPayment: (payload: {
    intent_id: string;
    payment_method: string;
    transaction_reference?: string;
    simulate_outcome?: "SUCCESS" | "FAILED";
  }) =>
    apiRequest<Payment>("/api/v1/finance/payments/process", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Refunds (Maker-Checker)
  getRefunds: () => apiRequest<RefundRequest[]>("/api/v1/finance/refunds"),
  requestRefund: (payload: { payment_id: string; amount: number; reason: string }) =>
    apiRequest<RefundRequest>("/api/v1/finance/refunds", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  approveRefund: (refundId: string) =>
    apiRequest<RefundRequest>(`/api/v1/finance/refunds/${refundId}/approve`, {
      method: "POST"
    }),
  rejectRefund: (refundId: string, reason: string) =>
    apiRequest<RefundRequest>(`/api/v1/finance/refunds/${refundId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason })
    }),

  // Reconciliation
  getReconciliationBatches: () => apiRequest<ReconciliationBatch[]>("/api/v1/finance/reconciliation/batches"),
  runReconciliation: (batchId: string) =>
    apiRequest<{ matched_count: number; discrepancy_count: number }>(
      `/api/v1/finance/reconciliation/batches/${batchId}/reconcile`,
      { method: "POST" }
    ),

  // Accounting & GL
  getTrialBalance: () => apiRequest<TrialBalance>("/api/v1/finance/accounting/trial-balance"),

  // Student Portal
  getStudentPortalOverview: () => apiRequest<StudentPortalOverview>("/api/v1/finance/portal/my-account")
};

