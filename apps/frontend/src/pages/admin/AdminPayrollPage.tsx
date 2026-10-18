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
  payrollApi,
  PayrollRun,
  PayrollPeriod,
  EmployeePayrollProfile,
  SalaryStructure
} from "../../features/payroll/api";
import {
  Banknote,
  Users,
  Calendar,
  CheckCircle2,
  FileCheck2,
  Send,
  Layers,
  ShieldCheck
} from "lucide-react";

export function AdminPayrollPage() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<"overview" | "profiles" | "periods" | "runs" | "disbursements">("overview");

  // Queries
  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ["admin", "payroll", "summary"],
    queryFn: () => payrollApi.getSummary()
  });

  const { data: profiles = [] } = useQuery({
    queryKey: ["admin", "payroll", "profiles"],
    queryFn: () => payrollApi.getProfiles()
  });

  const { data: structures = [] } = useQuery({
    queryKey: ["admin", "payroll", "structures"],
    queryFn: () => payrollApi.getStructures()
  });

  const { data: periods = [] } = useQuery({
    queryKey: ["admin", "payroll", "periods"],
    queryFn: () => payrollApi.getPeriods()
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["admin", "payroll", "runs"],
    queryFn: () => payrollApi.getRuns()
  });

  const { data: disbursements = [] } = useQuery({
    queryKey: ["admin", "payroll", "disbursements"],
    queryFn: () => payrollApi.getDisbursements()
  });

  // State for calculation
  const [selectedPeriodId, setSelectedPeriodId] = useState<string>("");

  // Mutations
  const calculateRunMutation = useMutation({
    mutationFn: (periodId: string) => payrollApi.calculateRun({ period_id: periodId }),
    onSuccess: (run) => {
      toast.push(`Payroll calculated! Gross: PKR ${Number(run.total_gross).toLocaleString()}, Net: PKR ${Number(run.total_net).toLocaleString()}`, "success");
      queryClient.invalidateQueries({ queryKey: ["admin", "payroll"] });
      setActiveTab("runs");
    },
    onError: (err: any) => {
      toast.push(err.message || "Failed to calculate payroll run.", "error");
    }
  });

  const approveRunMutation = useMutation({
    mutationFn: (runId: string) => payrollApi.approveRun(runId),
    onSuccess: () => {
      toast.push("Payroll run approved successfully (Maker-Checker verified)!", "success");
      queryClient.invalidateQueries({ queryKey: ["admin", "payroll"] });
    },
    onError: (err: any) => {
      toast.push(err.message || "Approval failed (Maker-Checker segregation violation).", "error");
    }
  });

  const executeDisbursementMutation = useMutation({
    mutationFn: (runId: string) =>
      payrollApi.executeDisbursement({ run_id: runId, payment_rail: "1bill_ach" }),
    onSuccess: (batch) => {
      toast.push(`Simulated disbursement executed for ${batch.total_records} employees!`, "success");
      queryClient.invalidateQueries({ queryKey: ["admin", "payroll"] });
      setActiveTab("disbursements");
    },
    onError: (err: any) => {
      toast.push(err.message || "Disbursement execution failed.", "error");
    }
  });

  if (isSummaryLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading payroll management workbench…" />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Staff Compensation & HR"
        title="Institutional Payroll & Disbursements"
        description="Calculate faculty salaries, gross-to-net withholdings, dual-control maker-checker payroll approvals, and execute simulated bank ACH disbursements."
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Enrolled Staff"
          value={String(summary?.total_employees ?? profiles.length)}
        />
        <StatCard
          label="Active Payroll Runs"
          value={String(summary?.active_runs_count ?? runs.length)}
        />
        <StatCard
          label="Last Net Payroll"
          value={`PKR ${Number(summary?.last_period_total_net || 0).toLocaleString()}`}
        />
        <StatCard
          label="YTD Disbursed (Simulated)"
          value={`PKR ${Number(summary?.ytd_total_disbursed || 0).toLocaleString()}`}
        />
      </div>

      {/* Tabs */}
      <div className="flex border-b mb-6 space-x-1 overflow-x-auto">
        {[
          { id: "overview", label: "Overview", icon: Banknote },
          { id: "profiles", label: "Staff & Salary Structures", icon: Users },
          { id: "periods", label: "Periods & Calculation Engine", icon: Calendar },
          { id: "runs", label: "Maker-Checker Approvals", icon: FileCheck2 },
          { id: "disbursements", label: "Simulated Disbursements", icon: Send }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2.5 px-4 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "border-primary-600 text-primary-600 bg-primary-50/50 dark:bg-primary-950/20"
                  : "border-transparent text-muted hover:text-foreground"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
              {tab.id === "runs" && runs.filter((r) => r.status === "CALCULATED").length > 0 && (
                <span className="ml-1 bg-amber-500 text-white rounded-full px-1.5 py-0.2 text-[10px]">
                  {runs.filter((r) => r.status === "CALCULATED").length}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab: Overview */}
      {activeTab === "overview" && (
        <Card className="p-6">
          <h3 className="text-base font-bold mb-2">Institutional Payroll Engine Health</h3>
          <p className="text-xs text-muted mb-4">
            Automated gross-to-net computation engine supports base pay, allowances (conveyance, medical, housing), statutory tax deductions, and unpaid leave proration. Maker-checker enforcement ensures segregation of duties prior to batch disbursement.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-muted/30 rounded border">
              <span className="text-xs text-muted">Configured Salary Structures</span>
              <div className="text-xl font-bold mt-1">{structures.length}</div>
            </div>
            <div className="p-4 bg-muted/30 rounded border">
              <span className="text-xs text-muted">Active Payroll Periods</span>
              <div className="text-xl font-bold mt-1">{periods.length}</div>
            </div>
            <div className="p-4 bg-muted/30 rounded border">
              <span className="text-xs text-muted">Maker-Checker Policy</span>
              <div className="flex items-center gap-2 mt-1">
                <ShieldCheck className="w-5 h-5 text-green-600" />
                <span className="font-bold text-green-600 text-sm">Enforced</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Tab: Profiles & Structures */}
      {activeTab === "profiles" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-5">
            <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
              <Users className="w-4 h-4 text-primary" />
              Enrolled Faculty & Staff Profiles
            </h3>
            <div className="space-y-3">
              {profiles.length === 0 ? (
                <p className="text-xs text-muted">No employee profiles enrolled.</p>
              ) : (
                profiles.map((p) => (
                  <div key={p.id} className="p-3 border rounded-lg bg-card space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-xs">{p.designation || "Faculty Member"}</span>
                      <Badge>
                        {p.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <div className="text-[11px] text-muted">
                      Dept: {p.department || "Computer Science"} · Emp ID: {p.employee_id.slice(0, 8)}…
                    </div>
                    <div className="text-[11px] font-mono text-muted">
                      Bank: {p.bank_name || "Meezan Bank"} (IBAN: {p.bank_iban ? `${p.bank_iban.slice(0, 6)}…` : "N/A"})
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary" />
              Configured Salary Structures
            </h3>
            <div className="space-y-3">
              {structures.length === 0 ? (
                <p className="text-xs text-muted">No salary structures configured.</p>
              ) : (
                structures.map((s) => (
                  <div key={s.id} className="p-3 border rounded-lg bg-card space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-xs">{s.name}</span>
                      <span className="font-mono font-bold text-xs">
                        Base: PKR {Number(s.base_salary).toLocaleString()}
                      </span>
                    </div>
                    <div className="pt-2 border-t grid grid-cols-2 gap-2 text-[11px]">
                      {s.components?.map((c, idx) => (
                        <div key={idx} className="flex justify-between">
                          <span className="text-muted">{c.name}:</span>
                          <span className={`font-mono ${c.component_type === "ALLOWANCE" ? "text-green-600" : "text-red-600"}`}>
                            {c.component_type === "ALLOWANCE" ? "+" : "-"}PKR {Number(c.amount).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Tab: Periods & Calculation Engine */}
      {activeTab === "periods" && (
        <Card className="p-6">
          <h3 className="text-base font-bold mb-2">Payroll Calculation Engine</h3>
          <p className="text-xs text-muted mb-4">
            Select a payroll period to trigger the automated gross-to-net salary calculator for all eligible faculty and staff members.
          </p>

          <div className="space-y-4 max-w-md mb-6">
            <div>
              <label className="text-xs font-semibold block mb-1">Select Payroll Period:</label>
              <select
                className="w-full text-xs p-2.5 border rounded bg-background"
                value={selectedPeriodId}
                onChange={(e) => setSelectedPeriodId(e.target.value)}
              >
                <option value="">-- Choose Period --</option>
                {periods.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({new Date(p.start_date).toLocaleDateString()} – {new Date(p.end_date).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>

            <Button
              className="text-xs px-3 py-1.5 min-h-8"
              onClick={() => calculateRunMutation.mutate(selectedPeriodId)}
              disabled={!selectedPeriodId || calculateRunMutation.isPending}
            >
              {calculateRunMutation.isPending ? "Calculating Salaries…" : "Run Calculation Engine"}
            </Button>
          </div>

          <h4 className="text-xs font-bold uppercase tracking-wider text-muted mb-2">Available Periods</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <th className="py-2.5 px-3">Period Name</th>
                  <th className="py-2.5 px-3">Start Date</th>
                  <th className="py-2.5 px-3">End Date</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {periods.map((p) => (
                  <tr key={p.id}>
                    <td className="py-2.5 px-3 font-medium">{p.name}</td>
                    <td className="py-2.5 px-3">{new Date(p.start_date).toLocaleDateString()}</td>
                    <td className="py-2.5 px-3">{new Date(p.end_date).toLocaleDateString()}</td>
                    <td className="py-2.5 px-3">
                      <Badge>
                        {p.is_closed ? "Closed" : "Open"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tab: Maker-Checker Run Approvals */}
      {activeTab === "runs" && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-primary" />
                Maker-Checker Payroll Approval Queue
              </h3>
              <p className="text-xs text-muted mt-1">
                Segregation of Duties: A payroll run created/calculated by one administrator cannot be approved by that same administrator.
              </p>
            </div>
          </div>

          {runs.length === 0 ? (
            <p className="text-xs text-muted text-center py-6">No payroll runs found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-muted/50 border-b">
                  <tr>
                    <th className="py-2.5 px-3">Period</th>
                    <th className="py-2.5 px-3">Total Gross</th>
                    <th className="py-2.5 px-3">Deductions</th>
                    <th className="py-2.5 px-3">Total Net</th>
                    <th className="py-2.5 px-3">Maker (Created By)</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {runs.map((r) => (
                    <tr key={r.id}>
                      <td className="py-2.5 px-3 font-medium">{r.period_name || "Monthly Period"}</td>
                      <td className="py-2.5 px-3 font-mono">PKR {Number(r.total_gross).toLocaleString()}</td>
                      <td className="py-2.5 px-3 font-mono text-red-600">-PKR {Number(r.total_deductions).toLocaleString()}</td>
                      <td className="py-2.5 px-3 font-mono font-bold text-green-600">PKR {Number(r.total_net).toLocaleString()}</td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-muted">{r.created_by?.slice(0, 8)}…</td>
                      <td className="py-2.5 px-3">
                        <Badge>
                          {r.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        {r.status === "CALCULATED" && (
                          <Button
                            variant="secondary"
                            className="text-xs px-2.5 py-1 min-h-8"
                            onClick={() => approveRunMutation.mutate(r.id)}
                            disabled={approveRunMutation.isPending}
                          >
                            Approve (Checker)
                          </Button>
                        )}
                        {r.status === "APPROVED" && (
                          <Button
                            className="text-xs px-2.5 py-1 min-h-8"
                            onClick={() => executeDisbursementMutation.mutate(r.id)}
                            disabled={executeDisbursementMutation.isPending}
                          >
                            Execute Disbursement
                          </Button>
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

      {/* Tab: Simulated Disbursements */}
      {activeTab === "disbursements" && (
        <Card className="p-6">
          <h3 className="text-base font-bold mb-2">Simulated Bank Disbursements & Rails</h3>
          <p className="text-xs text-muted mb-4">
            Disbursement batches executed via simulated direct ACH/1Bill payment rail with fail-closed safety. All employee payslips are generated and unlocked upon completion.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <th className="py-2.5 px-3">Batch ID</th>
                  <th className="py-2.5 px-3">Rail</th>
                  <th className="py-2.5 px-3">Total Amount</th>
                  <th className="py-2.5 px-3">Records</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y font-mono">
                {disbursements.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-6 text-muted font-sans">
                      No disbursement batches executed yet.
                    </td>
                  </tr>
                ) : (
                  disbursements.map((d) => (
                    <tr key={d.id}>
                      <td className="py-2.5 px-3 font-bold">{d.id.slice(0, 8)}…</td>
                      <td className="py-2.5 px-3 uppercase text-[11px] font-sans">{d.payment_rail}</td>
                      <td className="py-2.5 px-3 font-bold text-green-600">PKR {Number(d.total_amount).toLocaleString()}</td>
                      <td className="py-2.5 px-3 font-sans">{d.total_records} payslips</td>
                      <td className="py-2.5 px-3 font-sans">
                        <Badge>{d.status}</Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
