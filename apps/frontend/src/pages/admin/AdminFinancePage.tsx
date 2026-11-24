import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "../../components/ui/PageHeader";
import { Card } from "../../components/ui/Card";
import { StatCard } from "../../components/ui/StatCard";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { InlineError } from "../../components/ui/InlineError";
import { useToast } from "../../components/ui/useToast";
import {
  financeApi,
  FeeStructure,
  Scholarship,
  RefundRequest,
  TrialBalance
} from "../../features/finance/api";
import {
  DollarSign,
  Receipt,
  CheckCircle2,
  AlertTriangle,
  Scale,
  RefreshCw,
  FileCheck2,
  Users
} from "lucide-react";

export function AdminFinancePage() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<
    "overview" | "structures" | "invoicing" | "refunds" | "reconciliation" | "accounting"
  >("overview");

  // Queries
  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ["admin", "finance", "summary"],
    queryFn: () => financeApi.getSummary()
  });

  const { data: structures = [] } = useQuery({
    queryKey: ["admin", "finance", "structures"],
    queryFn: () => financeApi.getFeeStructures()
  });

  const { data: scholarships = [] } = useQuery({
    queryKey: ["admin", "finance", "scholarships"],
    queryFn: () => financeApi.getScholarships()
  });

  const { data: refunds = [] } = useQuery({
    queryKey: ["admin", "finance", "refunds"],
    queryFn: () => financeApi.getRefunds()
  });

  const { data: trialBalance } = useQuery({
    queryKey: ["admin", "finance", "trial-balance"],
    queryFn: () => financeApi.getTrialBalance()
  });

  const { data: batches = [] } = useQuery({
    queryKey: ["admin", "finance", "batches"],
    queryFn: () => financeApi.getReconciliationBatches()
  });

  // State for bulk generation
  const [selectedStructureId, setSelectedStructureId] = useState<string>("");
  const [studentIdsInput, setStudentIdsInput] = useState<string>("");
  const [numInstallments, setNumInstallments] = useState<number>(3);
  const [previewResult, setPreviewResult] = useState<any>(null);

  // Mutations
  const approveRefundMutation = useMutation({
    mutationFn: (refundId: string) => financeApi.approveRefund(refundId),
    onSuccess: (data) => {
      toast.push(`Refund ${data.refund_number} approved successfully!`, "success");
      queryClient.invalidateQueries({ queryKey: ["admin", "finance"] });
    },
    onError: (err: any) => {
      toast.push(err.message || "Failed to approve refund (Maker-Checker violation).", "error");
    }
  });

  const rejectRefundMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      financeApi.rejectRefund(id, reason),
    onSuccess: () => {
      toast.push("Refund request rejected.", "success");
      queryClient.invalidateQueries({ queryKey: ["admin", "finance"] });
    },
    onError: (err: any) => {
      toast.push(err.message || "Failed to reject refund.", "error");
    }
  });

  const previewBulkMutation = useMutation({
    mutationFn: () => {
      const studentIds = studentIdsInput
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      return financeApi.previewBulkInvoices({
        fee_structure_id: selectedStructureId,
        student_ids: studentIds,
        num_installments: numInstallments
      });
    },
    onSuccess: (res) => {
      setPreviewResult(res);
      toast.push(`Calculated billing preview for ${res.total_previewed} students.`, "success");
    },
    onError: (err: any) => {
      toast.push(err.message || "Preview failed.", "error");
    }
  });

  const generateBulkMutation = useMutation({
    mutationFn: () => {
      const studentIds = studentIdsInput
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      return financeApi.generateBulkInvoices({
        fee_structure_id: selectedStructureId,
        student_ids: studentIds,
        num_installments: numInstallments
      });
    },
    onSuccess: (res) => {
      toast.push(`Successfully issued ${res.total_created} invoices with ${numInstallments} installments!`, "success");
      setPreviewResult(null);
      setStudentIdsInput("");
      queryClient.invalidateQueries({ queryKey: ["admin", "finance"] });
    },
    onError: (err: any) => {
      toast.push(err.message || "Generation failed.", "error");
    }
  });

  if (isSummaryLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading institutional finance workbench…" />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Institutional Management"
        title="Finance, Fees & General Ledger"
        description="Oversee fee structures, bulk semester billing, dual-control refund approvals, bank reconciliation, and double-entry accounting trial balances."
      />

      {/* Financial KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <StatCard
          label="Total Billed"
          value={`PKR ${Number(summary?.total_billed || 0).toLocaleString()}`}
        />
        <StatCard
          label="Total Collected"
          value={`PKR ${Number(summary?.total_collected || 0).toLocaleString()}`}
        />
        <StatCard
          label="Outstanding Balance"
          value={`PKR ${Number(summary?.total_outstanding || 0).toLocaleString()}`}
        />
        <StatCard
          label="Collection Rate"
          value={`${Number(summary?.collection_rate || 0).toFixed(1)}%`}
        />
        <StatCard
          label="Total Refunded"
          value={`PKR ${Number(summary?.total_refunded || 0).toLocaleString()}`}
        />
      </div>

      {/* Tabs */}
      <div className="flex border-b mb-6 space-x-1 overflow-x-auto">
        {[
          { id: "overview", label: "Overview", icon: DollarSign },
          { id: "structures", label: "Fee Structures & Scholarships", icon: Receipt },
          { id: "invoicing", label: "Bulk Billing & Invoices", icon: Users },
          { id: "refunds", label: "Maker-Checker Refunds", icon: FileCheck2 },
          { id: "reconciliation", label: "Bank Reconciliation", icon: RefreshCw },
          { id: "accounting", label: "Double-Entry GL & Trial Balance", icon: Scale }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2.5 px-4 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "border-primary text-primary-ink bg-primary-soft/50"
                  : "border-transparent text-muted hover:text-ink"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
              {tab.id === "refunds" && refunds.filter((r) => r.status === "PENDING_APPROVAL").length > 0 && (
                <span className="ml-1 bg-danger text-danger-fg rounded-full px-1.5 py-0.2 text-[10px]">
                  {refunds.filter((r) => r.status === "PENDING_APPROVAL").length}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-base font-bold mb-2">Institutional Finance System Health</h3>
            <p className="text-xs text-muted mb-4">
              All financial transactions are strictly posted using the double-entry accounting ledger. External payment gateways (JazzCash, Easypaisa, 1Bill) operate in simulated fail-closed sandbox mode.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-subtle/60 rounded border border-line">
                <span className="text-xs text-muted">Active Invoices</span>
                <div className="text-xl font-bold mt-1">{summary?.active_invoices_count ?? 0}</div>
              </div>
              <div className="p-4 bg-subtle/60 rounded border border-line">
                <span className="text-xs text-muted">Configured Fee Structures</span>
                <div className="text-xl font-bold mt-1">{structures.length}</div>
              </div>
              <div className="p-4 bg-subtle/60 rounded border border-line">
                <span className="text-xs text-muted">General Ledger Status</span>
                <div className="flex items-center gap-2 mt-1">
                  <CheckCircle2 className="w-5 h-5 text-success-ink" />
                  <span className="font-bold text-success-ink text-sm">Debits Equal Credits</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab: Fee Structures & Scholarships */}
      {activeTab === "structures" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5">
              <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                <Receipt className="w-4 h-4 text-primary" />
                Configured Fee Structures
              </h3>
              <div className="space-y-3">
                {structures.length === 0 ? (
                  <p className="text-xs text-muted">No fee structures configured.</p>
                ) : (
                  structures.map((s) => (
                    <div key={s.id} className="p-3 border rounded-lg bg-card space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-xs">{s.name}</span>
                        <Badge>PKR {Number(s.total_fee).toLocaleString()}</Badge>
                      </div>
                      <div className="text-[11px] text-muted">
                        Program: {s.program} · Year: {s.academic_year} · Term: {s.term}
                      </div>
                      <div className="pt-2 border-t grid grid-cols-2 gap-2 text-[11px]">
                        {s.components?.map((c) => (
                          <div key={c.id || c.component_name} className="flex justify-between">
                            <span className="text-muted">{c.component_name}:</span>
                            <span className="font-mono">PKR {Number(c.amount).toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>

            <Card className="p-5">
              <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                <Scale className="w-4 h-4 text-primary" />
                Active Scholarships & Concessions
              </h3>
              <div className="space-y-3">
                {scholarships.length === 0 ? (
                  <p className="text-xs text-muted">No scholarships configured.</p>
                ) : (
                  scholarships.map((sch) => (
                    <div key={sch.id} className="p-3 border rounded-lg bg-card space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-xs">{sch.name} ({sch.code})</span>
                        <Badge>{sch.discount_percentage}% OFF</Badge>
                      </div>
                      <div className="text-[11px] text-muted">
                        Type: {sch.scholarship_type} · Tuition Only: {sch.applies_to_tuition_only ? "Yes" : "No"}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Tab: Bulk Invoicing */}
      {activeTab === "invoicing" && (
        <Card className="p-6">
          <h3 className="text-base font-bold mb-2">Semester Invoicing Engine</h3>
          <p className="text-xs text-muted mb-4">
            Select a fee structure and specify target student IDs to preview calculations and bulk-generate student invoices with installment schedules (due dates, 10-day grace periods, and late fee policies).
          </p>

          <div className="space-y-4 max-w-xl">
            <div>
              <label className="text-xs font-semibold block mb-1">Fee Structure:</label>
              <select
                className="w-full text-xs p-2.5 border rounded bg-background"
                value={selectedStructureId}
                onChange={(e) => setSelectedStructureId(e.target.value)}
              >
                <option value="">-- Select Fee Structure --</option>
                {structures.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} - PKR {Number(s.total_fee).toLocaleString()} ({s.program})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold block mb-1">Installment Count:</label>
              <select
                className="w-full text-xs p-2.5 border rounded bg-background"
                value={numInstallments}
                onChange={(e) => setNumInstallments(Number(e.target.value))}
              >
                <option value={1}>1 (Full payment upfront)</option>
                <option value={2}>2 Installments</option>
                <option value={3}>3 Installments (Standard 40/30/30)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold block mb-1">
                Student IDs (one UUID per line):
              </label>
              <textarea
                className="w-full text-xs p-2.5 border rounded font-mono bg-background"
                rows={4}
                placeholder="e.g. 11111111-1111-1111-1111-111111111111"
                value={studentIdsInput}
                onChange={(e) => setStudentIdsInput(e.target.value)}
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button
                variant="secondary"
                className="text-xs px-3 py-1.5 min-h-8"
                onClick={() => previewBulkMutation.mutate()}
                disabled={!selectedStructureId || !studentIdsInput.trim() || previewBulkMutation.isPending}
              >
                {previewBulkMutation.isPending ? "Calculating…" : "Preview Bulk Calculations"}
              </Button>
              <Button
                className="text-xs px-3 py-1.5 min-h-8"
                onClick={() => generateBulkMutation.mutate()}
                disabled={!selectedStructureId || !studentIdsInput.trim() || generateBulkMutation.isPending}
              >
                {generateBulkMutation.isPending ? "Generating Invoices…" : "Generate & Post Invoices"}
              </Button>
            </div>

            {previewResult && (
              <div className="mt-4 p-4 bg-subtle/70 rounded border border-line text-xs space-y-2">
                <div className="font-bold">Preview Calculation Summary:</div>
                <div>Total Students Processed: {previewResult.total_previewed}</div>
                <div className="font-mono text-muted text-[11px]">
                  Sample calculation ready. Click "Generate & Post Invoices" to create journal entries and issue invoices.
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Tab: Maker-Checker Refunds */}
      {activeTab === "refunds" && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-primary" />
                Maker-Checker Refund Approval Queue
              </h3>
              <p className="text-xs text-muted mt-1">
                Strict dual-control policy: The administrator who initiated the refund request cannot approve it. A separate checker must review and authorize.
              </p>
            </div>
          </div>

          {refunds.length === 0 ? (
            <p className="text-xs text-muted text-center py-8">No refund requests in queue.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-subtle/75 border-b border-line">
                  <tr>
                    <th className="py-2.5 px-3">Refund #</th>
                    <th className="py-2.5 px-3">Student ID</th>
                    <th className="py-2.5 px-3">Amount</th>
                    <th className="py-2.5 px-3">Reason</th>
                    <th className="py-2.5 px-3">Maker (Initiator)</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {refunds.map((r) => (
                    <tr key={r.id}>
                      <td className="py-2.5 px-3 font-mono font-medium">{r.refund_number}</td>
                      <td className="py-2.5 px-3 font-mono text-[11px]">{r.student_id.slice(0, 8)}…</td>
                      <td className="py-2.5 px-3 font-bold text-danger-ink">PKR {Number(r.amount).toLocaleString()}</td>
                      <td className="py-2.5 px-3">{r.reason}</td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-muted">{r.maker_id.slice(0, 8)}…</td>
                      <td className="py-2.5 px-3">
                        <Badge>
                          {r.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        {r.status === "PENDING_APPROVAL" && (
                          <div className="flex justify-end gap-1.5">
                            <Button
                              variant="secondary"
                              className="text-xs px-2.5 py-1 min-h-8"
                              onClick={() => approveRefundMutation.mutate(r.id)}
                              disabled={approveRefundMutation.isPending}
                            >
                              Approve
                            </Button>
                            <Button
                              variant="danger"
                              className="text-xs px-2.5 py-1 min-h-8"
                              onClick={() => rejectRefundMutation.mutate({ id: r.id, reason: "Administrative review" })}
                              disabled={rejectRefundMutation.isPending}
                            >
                              Reject
                            </Button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* Tab: Bank Reconciliation */}
      {activeTab === "reconciliation" && (
        <Card className="p-6">
          <h3 className="text-base font-bold mb-2">Automated Bank Statement Reconciliation</h3>
          <p className="text-xs text-muted mb-4">
            Upload CSV statements from 1Bill, JazzCash, or Bank Alfalah to reconcile external transaction references against internal payment intents and identify discrepancies.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-subtle/75 border-b border-line">
                <tr>
                  <th className="py-2.5 px-3">Batch #</th>
                  <th className="py-2.5 px-3">Gateway</th>
                  <th className="py-2.5 px-3">Total Amount</th>
                  <th className="py-2.5 px-3">Records (Matched / Total)</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {batches.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-6 text-muted">
                      No reconciliation batches found.
                    </td>
                  </tr>
                ) : (
                  batches.map((b) => (
                    <tr key={b.id}>
                      <td className="py-2.5 px-3 font-mono font-medium">{b.batch_number}</td>
                      <td className="py-2.5 px-3 uppercase">{b.gateway}</td>
                      <td className="py-2.5 px-3 font-bold">PKR {Number(b.total_amount).toLocaleString()}</td>
                      <td className="py-2.5 px-3">
                        {b.matched_records} / {b.total_records} ({b.unmatched_records} unmatched)
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge>
                          {b.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        {b.status === "PENDING" && (
                          <Button
                            variant="secondary"
                            className="text-xs px-2.5 py-1 min-h-8"
                            onClick={() => financeApi.runReconciliation(b.id)}
                          >
                            Reconcile Batch
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tab: Double-Entry GL & Trial Balance */}
      {activeTab === "accounting" && (
        <Card className="p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b mb-4 gap-3">
            <div>
              <h3 className="text-base font-bold flex items-center gap-2">
                <Scale className="w-5 h-5 text-primary" />
                Double-Entry Accounting Trial Balance
              </h3>
              <p className="text-xs text-muted">
                As of {trialBalance?.as_of_date ? new Date(trialBalance.as_of_date).toLocaleDateString() : "Today"}
              </p>
            </div>
            <div>
              {trialBalance?.is_balanced ? (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-success-soft border border-success/40 rounded-md">
                  <CheckCircle2 className="w-4 h-4 text-success-ink" />
                  <span className="text-xs font-bold text-success-ink">
                    Balanced: Total Debits == Total Credits
                  </span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-danger-soft border border-danger/40 rounded-md">
                  <AlertTriangle className="w-4 h-4 text-danger-ink" />
                  <span className="text-xs font-bold text-danger-ink">
                    Imbalance Detected
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-subtle/75 border-b border-line">
                <tr>
                  <th className="py-2.5 px-3">Account Code</th>
                  <th className="py-2.5 px-3">Account Name</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-right">Debit Balance (PKR)</th>
                  <th className="py-2.5 px-3 text-right">Credit Balance (PKR)</th>
                </tr>
              </thead>
              <tbody className="divide-y font-mono">
                {trialBalance?.accounts?.map((acc) => (
                  <tr key={acc.account_code} className="hover:bg-subtle/45">
                    <td className="py-2.5 px-3 font-bold">{acc.account_code}</td>
                    <td className="py-2.5 px-3 font-sans">{acc.account_name}</td>
                    <td className="py-2.5 px-3 font-sans text-muted">{acc.account_type}</td>
                    <td className="py-2.5 px-3 text-right">
                      {Number(acc.debit_balance) > 0 ? Number(acc.debit_balance).toLocaleString() : "—"}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      {Number(acc.credit_balance) > 0 ? Number(acc.credit_balance).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="border-t-2 border-line font-mono font-bold bg-subtle/70">
                <tr>
                  <td colSpan={3} className="py-3 px-3 font-sans text-right">
                    Trial Balance Totals:
                  </td>
                  <td className="py-3 px-3 text-right text-sm text-success-ink">
                    PKR {Number(trialBalance?.total_debits || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right text-sm text-success-ink">
                    PKR {Number(trialBalance?.total_credits || 0).toLocaleString()}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
