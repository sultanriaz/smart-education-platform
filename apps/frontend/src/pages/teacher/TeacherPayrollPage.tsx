import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "../../components/ui/PageHeader";
import { Card } from "../../components/ui/Card";
import { StatCard } from "../../components/ui/StatCard";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { InlineError } from "../../components/ui/InlineError";
import { useToast } from "../../components/ui/useToast";
import { payrollApi, Payslip } from "../../features/payroll/api";
import { Download, Calendar, ShieldCheck } from "lucide-react";

export function TeacherPayrollPage() {
  const toast = useToast();
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);

  const { data: payslips = [], isLoading, isFetching, error, refetch } = useQuery({
    queryKey: ["teacher", "payroll", "my-payslips"],
    queryFn: () => payrollApi.getMyPayslips()
  });

  if (isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading your payroll payslips and compensation records…" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher Portal" title="My Payslips & Compensation" />
        <InlineError
          message="Could not load your staff payroll records."
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      </div>
    );
  }

  const latestPayslip = payslips[0];

  const handleDownload = (payslip: Payslip) => {
    toast.push(`Payslip for ${payslip.period_name} downloaded successfully (simulated PDF).`, "success");
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Faculty & Staff Portal"
        title="My Payslips & Compensation"
        description="View your monthly salary statements, gross compensation, tax and provident fund deductions, and net disbursements."
      />

      {/* Summary KPI row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Latest Net Salary"
          value={latestPayslip ? `PKR ${Number(latestPayslip.net_salary).toLocaleString()}` : "N/A"}
        />
        <StatCard
          label="Latest Gross Pay"
          value={latestPayslip ? `PKR ${Number(latestPayslip.gross_salary).toLocaleString()}` : "N/A"}
        />
        <StatCard
          label="Total Deductions"
          value={latestPayslip ? `PKR ${Number(latestPayslip.total_deductions).toLocaleString()}` : "N/A"}
        />
        <StatCard
          label="Disbursement Status"
          value={latestPayslip ? latestPayslip.disbursement_status : "N/A"}
        />
      </div>

      {/* Payslips List */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold">Salary Slip Statements</h3>
        </div>

        {payslips.length === 0 ? (
          <EmptyState
            title="No payslips available yet"
            description="Payroll statements and salary slips generated for your faculty profile will appear here."
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-3">
              {payslips.map((p) => (
                <div
                  key={p.id}
                  className={`panel p-4 transition-all cursor-pointer hover:border-primary/60 ${
                    selectedPayslip?.id === p.id ? "border-primary bg-primary-soft/50" : ""
                  }`}
                  onClick={() => setSelectedPayslip(p)}
                >
                  <div className="flex justify-between items-center">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-primary" />
                        <span className="font-bold text-sm">{p.period_name}</span>
                        <Badge>
                          {p.disbursement_status}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted">
                        Generated on {new Date(p.generated_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-success-ink">
                        PKR {Number(p.net_salary).toLocaleString()}
                      </div>
                      <div className="text-[11px] text-muted">
                        Gross: PKR {Number(p.gross_salary).toLocaleString()} · Ded: PKR {Number(p.total_deductions).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Selected Payslip Detail Pane */}
            <div>
              {selectedPayslip ? (
                <Card className="p-5 border-primary/40 sticky top-4">
                  <div className="flex justify-between items-start border-b pb-3 mb-3">
                    <div>
                      <h4 className="font-bold text-sm">Payslip Breakdown</h4>
                      <p className="text-xs text-muted">{selectedPayslip.period_name}</p>
                    </div>
                    <Button
                      variant="secondary"
                      onClick={() => handleDownload(selectedPayslip)}
                      className="flex items-center gap-1.5 text-xs px-2.5 py-1 min-h-8"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </Button>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="bg-subtle/70 p-3 rounded space-y-1.5">
                      <div className="flex justify-between">
                        <span className="text-muted">Status:</span>
                        <Badge>
                          {selectedPayslip.disbursement_status}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted">Payment Rail:</span>
                        <span className="font-semibold">Simulated 1Bill Direct ACH</span>
                      </div>
                    </div>

                    <div className="border-t pt-2 space-y-1.5">
                      <div className="font-semibold text-muted uppercase text-[10px] tracking-wider">Earnings</div>
                      <div className="flex justify-between">
                        <span>Base Salary</span>
                        <span className="font-mono">PKR {Number(selectedPayslip.gross_salary - selectedPayslip.total_allowances).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Allowances (House, Med)</span>
                        <span className="font-mono text-success-ink">+PKR {Number(selectedPayslip.total_allowances).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between font-bold pt-1 border-t">
                        <span>Total Gross</span>
                        <span className="font-mono">PKR {Number(selectedPayslip.gross_salary).toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="border-t pt-2 space-y-1.5">
                      <div className="font-semibold text-muted uppercase text-[10px] tracking-wider">Deductions</div>
                      <div className="flex justify-between">
                        <span>Statutory & Tax Withholdings</span>
                        <span className="font-mono text-danger-ink">-PKR {Number(selectedPayslip.total_deductions).toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="border-t-2 pt-3 flex justify-between items-center text-sm font-bold">
                      <span>Net Disbursed:</span>
                      <span className="text-success-ink font-mono text-base">
                        PKR {Number(selectedPayslip.net_salary).toLocaleString()}
                      </span>
                    </div>

                    <div className="bg-primary-soft p-2.5 rounded text-[11px] text-primary-ink flex items-start gap-2 mt-4">
                      <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>This payslip was verified and certified by Institution Finance & Accounts.</span>
                    </div>
                  </div>
                </Card>
              ) : (
                <Card className="p-6 text-center text-muted">
                  <p className="text-xs">Select any payslip from the list to view its complete earnings and deduction breakdown.</p>
                </Card>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
