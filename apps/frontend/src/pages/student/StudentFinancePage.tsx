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
import { financeApi, Invoice, InvoiceInstallment } from "../../features/finance/api";
import { AlertCircle, CreditCard, ShieldCheck, X } from "lucide-react";

export function StudentFinancePage() {
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: portal, isLoading, isFetching, error, refetch } = useQuery({
    queryKey: ["student", "finance", "portal"],
    queryFn: () => financeApi.getStudentPortalOverview()
  });

  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [selectedInstallment, setSelectedInstallment] = useState<InvoiceInstallment | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<string>("jazzcash");
  const [isPayModalOpen, setIsPayModalOpen] = useState(false);

  const processPaymentMutation = useMutation({
    mutationFn: async () => {
      if (!portal?.account?.student_id || !selectedInvoice) {
        throw new Error("Missing invoice or student details");
      }
      const amountToPay = selectedInstallment
        ? (selectedInstallment.amount_due + selectedInstallment.late_fee_amount - selectedInstallment.paid_amount)
        : selectedInvoice.balance_amount;

      // 1. Create intent
      const intent = await financeApi.createPaymentIntent({
        student_id: portal.account.student_id,
        invoice_id: selectedInvoice.id,
        installment_id: selectedInstallment?.id,
        amount: amountToPay,
        payment_method: paymentMethod
      });

      // 2. Process simulated payment
      const payment = await financeApi.processPayment({
        intent_id: intent.intent_id,
        payment_method: paymentMethod,
        simulate_outcome: "SUCCESS"
      });

      return payment;
    },
    onSuccess: (payment) => {
      toast.push(`Payment ${payment.payment_number} completed successfully!`, "success");
      setIsPayModalOpen(false);
      setSelectedInvoice(null);
      setSelectedInstallment(null);
      queryClient.invalidateQueries({ queryKey: ["student", "finance"] });
    },
    onError: (err: any) => {
      toast.push(err.message || "Payment processing failed.", "error");
    }
  });

  if (isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading student fee and financial account details…" />
      </div>
    );
  }

  if (error || !portal) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Student" title="Fee & Payments" />
        <InlineError
          message="Could not load your student financial profile."
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      </div>
    );
  }

  const { account, invoices = [], payments = [], scholarships = [] } = portal;

  const handleOpenPayment = (inv: Invoice, inst?: InvoiceInstallment) => {
    setSelectedInvoice(inv);
    setSelectedInstallment(inst || null);
    setIsPayModalOpen(true);
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student Finance Portal"
        title="My Fees, Invoices & Payments"
        description="View your semester fee structure, installment due dates, scholarship concessions, and make secure simulated payments."
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Total Billed"
          value={`PKR ${Number(account.total_billed || 0).toLocaleString()}`}
        />
        <StatCard
          label="Total Paid"
          value={`PKR ${Number(account.total_paid || 0).toLocaleString()}`}
        />
        <StatCard
          label="Scholarship Concession"
          value={`PKR ${Number(account.total_discounted || 0).toLocaleString()}`}
        />
        <StatCard
          label="Current Outstanding"
          value={`PKR ${Number(account.current_balance || 0).toLocaleString()}`}
        />
      </div>

      {/* Scholarships Notice if any */}
      {scholarships.length > 0 && (
        <Card className="mb-6 border-l-4 border-l-primary p-4">
          <div className="flex items-center gap-3">
            <ShieldCheck className="text-primary-ink h-6 w-6" />
            <div>
              <h4 className="font-semibold text-sm text-ink">Active Scholarships / Fee Concessions</h4>
              <p className="text-xs text-muted">
                {scholarships.map((s) => `${s.name} (${s.discount_percentage}% discount)`).join(", ")}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Invoices and Installments */}
      <div className="space-y-6 mb-8">
        <h3 className="text-lg font-bold">Fee Invoices & Installment Plans</h3>
        {invoices.length === 0 ? (
          <Card className="p-6 text-center text-muted">
            <p>No active fee invoices issued for this academic semester.</p>
          </Card>
        ) : (
          invoices.map((inv) => (
            <Card key={inv.id} className="p-5">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base">{inv.invoice_number}</span>
                    <Badge>
                      {inv.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-muted mt-1">
                    Issued: {new Date(inv.created_at).toLocaleDateString()} · Due: {new Date(inv.due_date).toLocaleDateString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold">Total: PKR {Number(inv.payable_amount).toLocaleString()}</div>
                  <div className="text-xs text-muted">Balance: PKR {Number(inv.balance_amount).toLocaleString()}</div>
                  {inv.status !== "PAID" && (
                    <Button
                      className="mt-2 text-xs px-3 py-2"
                      onClick={() => handleOpenPayment(inv)}
                    >
                      Pay Full Balance
                    </Button>
                  )}
                </div>
              </div>

              {/* Installments Table */}
              {inv.installments && inv.installments.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Installment Schedule</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-subtle/60 text-muted">
                        <tr>
                          <th className="py-2 px-3">#</th>
                          <th className="py-2 px-3">Due Date</th>
                          <th className="py-2 px-3">Grace Ends</th>
                          <th className="py-2 px-3">Amount Due</th>
                          <th className="py-2 px-3">Late Fee</th>
                          <th className="py-2 px-3">Paid</th>
                          <th className="py-2 px-3">Status</th>
                          <th className="py-2 px-3 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {inv.installments.map((inst) => (
                          <tr key={inst.id} className="hover:bg-subtle/45">
                            <td className="py-2 px-3 font-medium">Inst. {inst.installment_number}</td>
                            <td className="py-2 px-3">{new Date(inst.due_date).toLocaleDateString()}</td>
                            <td className="py-2 px-3">{new Date(inst.grace_period_end_date).toLocaleDateString()}</td>
                            <td className="py-2 px-3">PKR {Number(inst.amount_due).toLocaleString()}</td>
                            <td className="py-2 px-3 text-danger-ink">
                              {inst.late_fee_amount > 0 ? `+PKR ${inst.late_fee_amount}` : "None"}
                            </td>
                            <td className="py-2 px-3">PKR {Number(inst.paid_amount).toLocaleString()}</td>
                            <td className="py-2 px-3">
                              <Badge>
                                {inst.status}
                              </Badge>
                            </td>
                            <td className="py-2 px-3 text-right">
                              {inst.status !== "PAID" && (
                                <Button
                                  variant="secondary"
                                  className="text-xs px-3 py-2"
                                  onClick={() => handleOpenPayment(inv, inst)}
                                >
                                  Pay Installment
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </Card>
          ))
        )}
      </div>

      {/* Payment History */}
      <div>
        <h3 className="text-lg font-bold mb-4">Payment Receipts & History</h3>
        {payments.length === 0 ? (
          <Card className="p-4 text-center text-muted">
            <p>No payment records found.</p>
          </Card>
        ) : (
          <div className="overflow-x-auto bg-card rounded-lg border">
            <table className="w-full text-xs text-left">
              <thead className="bg-subtle/75 border-b border-line">
                <tr>
                  <th className="py-2.5 px-4">Receipt #</th>
                  <th className="py-2.5 px-4">Date</th>
                  <th className="py-2.5 px-4">Method</th>
                  <th className="py-2.5 px-4">Reference</th>
                  <th className="py-2.5 px-4">Amount</th>
                  <th className="py-2.5 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {payments.map((p) => (
                  <tr key={p.id}>
                    <td className="py-2.5 px-4 font-mono font-medium">{p.payment_number}</td>
                    <td className="py-2.5 px-4">{new Date(p.created_at).toLocaleDateString()}</td>
                    <td className="py-2.5 px-4 uppercase">{p.payment_method}</td>
                    <td className="py-2.5 px-4 font-mono text-muted">{p.gateway_reference || "N/A"}</td>
                    <td className="py-2.5 px-4 font-bold text-success-ink">PKR {Number(p.amount).toLocaleString()}</td>
                    <td className="py-2.5 px-4">
                      <Badge>{p.status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Simulated Payment Modal */}
      {isPayModalOpen && selectedInvoice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 p-4 backdrop-blur-xs">
          <div className="bg-panel text-ink rounded-lg shadow-xl max-w-md w-full p-6 border border-line space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-base font-bold flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-primary" />
                Simulated Fee Payment Checkout
              </h3>
              <button
                type="button"
                aria-label="Close payment modal"
                className="inline-flex h-11 w-11 items-center justify-center rounded-lg text-muted hover:text-ink transition"
                onClick={() => setIsPayModalOpen(false)}
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            <div className="bg-subtle/60 p-3 rounded-md space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-muted">Invoice:</span>
                <span className="font-semibold">{selectedInvoice.invoice_number}</span>
              </div>
              {selectedInstallment && (
                <div className="flex justify-between">
                  <span className="text-muted">Installment:</span>
                  <span className="font-semibold">Installment #{selectedInstallment.installment_number}</span>
                </div>
              )}
              <div className="flex justify-between text-sm font-bold pt-2 border-t mt-2">
                <span>Amount Payable:</span>
                <span className="text-primary-ink font-semibold">
                  PKR{" "}
                  {Number(
                    selectedInstallment
                      ? selectedInstallment.amount_due + selectedInstallment.late_fee_amount - selectedInstallment.paid_amount
                      : selectedInvoice.balance_amount
                  ).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold">Select Payment Gateway / Method:</label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { id: "jazzcash", name: "JazzCash (HMAC)" },
                  { id: "easypaisa", name: "Easypaisa" },
                  { id: "bank_transfer", name: "1Bill / Bank Transfer" },
                  { id: "cash", name: "Cash Voucher" }
                ].map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setPaymentMethod(m.id)}
                    className={`p-3 border rounded text-left transition-all ${
                      paymentMethod === m.id
                        ? "border-primary bg-primary-soft text-primary-ink font-bold"
                        : "border-line hover:bg-subtle/60"
                    }`}
                  >
                    {m.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="text-[11px] text-warning-ink bg-warning-soft p-2.5 rounded border border-warning/35 flex gap-2">
              <AlertCircle className="w-4 h-4 text-warning-ink shrink-0 mt-0.5" />
              <span>
                <strong>Test Sandbox Environment:</strong> Payments are processed via simulated banking rails with SHA-256 HMAC cryptographic signatures. Real money is never transferred.
              </span>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="secondary"
                className="text-xs px-3 py-1.5 min-h-8"
                onClick={() => setIsPayModalOpen(false)}
                disabled={processPaymentMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                className="text-xs px-3 py-1.5 min-h-8"
                onClick={() => processPaymentMutation.mutate()}
                disabled={processPaymentMutation.isPending}
              >
                {processPaymentMutation.isPending ? "Simulating Transfer…" : "Authorize & Pay"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
