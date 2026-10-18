import { apiRequest } from "../../lib/api-client";

export interface EmployeePayrollProfile {
  id: string;
  employee_id: string;
  bank_name?: string;
  bank_account_number?: string;
  bank_iban?: string;
  designation?: string;
  department?: string;
  is_active: boolean;
}

export interface SalaryComponent {
  id?: string;
  name: string;
  component_type: "ALLOWANCE" | "DEDUCTION";
  amount: number;
  is_taxable: boolean;
}

export interface SalaryStructure {
  id: string;
  name: string;
  base_salary: number;
  currency: string;
  components: SalaryComponent[];
}

export interface PayrollPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  is_closed: boolean;
}

export interface PayrollRunItem {
  id: string;
  employee_id: string;
  base_salary: number;
  gross_salary: number;
  total_allowances: number;
  total_deductions: number;
  net_salary: number;
  is_prorated: boolean;
}

export interface PayrollRun {
  id: string;
  period_id: string;
  period_name?: string;
  status: "DRAFT" | "CALCULATED" | "APPROVED" | "DISBURSED" | "CANCELLED";
  total_gross: number;
  total_deductions: number;
  total_net: number;
  created_by: string;
  approved_by?: string;
  created_at: string;
  items?: PayrollRunItem[];
}

export interface Payslip {
  id: string;
  run_item_id: string;
  employee_id: string;
  period_name: string;
  gross_salary: number;
  total_allowances: number;
  total_deductions: number;
  net_salary: number;
  disbursement_status: string;
  generated_at: string;
  breakdown?: {
    base_salary: number;
    allowances: Record<string, number>;
    deductions: Record<string, number>;
  };
}

export interface DisbursementBatch {
  id: string;
  run_id: string;
  payment_rail: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  total_amount: number;
  total_records: number;
  processed_at?: string;
}

export interface PayrollSummary {
  total_employees: number;
  active_runs_count: number;
  last_period_total_net: number;
  ytd_total_disbursed: number;
}

export const payrollApi = {
  getSummary: () => apiRequest<PayrollSummary>("/api/v1/payroll/reports/summary"),

  // Employee Profiles
  getProfiles: () => apiRequest<EmployeePayrollProfile[]>("/api/v1/payroll/profiles"),
  createProfile: (payload: {
    employee_id: string;
    bank_name?: string;
    bank_account_number?: string;
    bank_iban?: string;
    designation?: string;
    department?: string;
  }) =>
    apiRequest<EmployeePayrollProfile>("/api/v1/payroll/profiles", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Salary Structures
  getStructures: () => apiRequest<SalaryStructure[]>("/api/v1/payroll/structures"),
  createStructure: (payload: {
    name: string;
    base_salary: number;
    components: SalaryComponent[];
  }) =>
    apiRequest<SalaryStructure>("/api/v1/payroll/structures", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  assignStructure: (payload: { employee_id: string; structure_id: string; effective_from: string }) =>
    apiRequest("/api/v1/payroll/structures/assign", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Periods
  getPeriods: () => apiRequest<PayrollPeriod[]>("/api/v1/payroll/periods"),
  createPeriod: (payload: { name: string; start_date: string; end_date: string }) =>
    apiRequest<PayrollPeriod>("/api/v1/payroll/periods", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  // Runs (with Maker-Checker approval)
  getRuns: () => apiRequest<PayrollRun[]>("/api/v1/payroll/runs"),
  getRunDetails: (runId: string) => apiRequest<PayrollRun>(`/api/v1/payroll/runs/${runId}`),
  calculateRun: (payload: { period_id: string }) =>
    apiRequest<PayrollRun>("/api/v1/payroll/runs", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  approveRun: (runId: string) =>
    apiRequest<PayrollRun>(`/api/v1/payroll/runs/${runId}/decision`, {
      method: "POST",
      body: JSON.stringify({ approved: true, notes: "Approved via Admin Payroll Workbench" })
    }),

  // Disbursements
  getDisbursements: () => apiRequest<DisbursementBatch[]>("/api/v1/payroll/disbursements/batches"),
  executeDisbursement: (payload: { run_id: string; payment_rail?: string }) =>
    apiRequest<DisbursementBatch>(`/api/v1/payroll/disbursements/runs/${payload.run_id}/disburse`, {
      method: "POST"
    }),

  // Self-service Payslips
  getMyPayslips: () => apiRequest<Payslip[]>("/api/v1/payroll/payslips/my-payslips"),
  getPayslipDetails: (payslipId: string) =>
    apiRequest<Payslip>(`/api/v1/payroll/payslips/${payslipId}`)
};
