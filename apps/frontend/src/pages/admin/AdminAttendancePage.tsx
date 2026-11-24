import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { InlineError } from "../../components/ui/InlineError";
import { useToast } from "../../components/ui/useToast";
import { apiRequest } from "../../lib/api-client";
import { useSections } from "../../features/admin/hooks";
import { Calendar, User, History, CheckCircle2 } from "lucide-react";

interface Session {
  id: string;
  section_id: string;
  session_date: string;
  status: string;
}

interface RecordRow {
  student_user_id: string;
  status: string;
  notes: string | null;
}

interface ChangeRow {
  action?: string;
  reason?: string;
  changed_at?: string;
  changed_by_user_id?: string;
}

async function pages<T>(base: string): Promise<T[]> {
  const results: T[] = [];
  for (let offset = 0; offset < 10000; offset += 100) {
    const suffix = `${base.includes("?") ? "&" : "?"}limit=100&offset=${offset}`;
    const batch = await apiRequest<T[]>(`${base}${suffix}`);
    results.push(...batch);
    if (batch.length < 100) return results;
  }
  throw new Error("Result exceeds permitted pagination bound.");
}

function statusBadge(status: string) {
  const s = status.toUpperCase();
  if (s === "PRESENT") {
    return <span className="inline-flex items-center rounded-full bg-success-soft px-2.5 py-0.5 text-xs font-semibold text-success-ink">Present</span>;
  }
  if (s === "ABSENT") {
    return <span className="inline-flex items-center rounded-full bg-danger-soft px-2.5 py-0.5 text-xs font-semibold text-danger-ink">Absent</span>;
  }
  if (s === "LATE") {
    return <span className="inline-flex items-center rounded-full bg-warning-soft px-2.5 py-0.5 text-xs font-semibold text-warning-ink">Late</span>;
  }
  return <span className="inline-flex items-center rounded-full bg-secondary-soft px-2.5 py-0.5 text-xs font-semibold text-secondary-ink">{status}</span>;
}

export function AdminAttendancePage() {
  const sections = useSections();
  const queryClient = useQueryClient();
  const toast = useToast();

  const [sectionId, setSectionId] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [reason, setReason] = useState("");
  const [studentId, setStudentId] = useState("");
  const [newStatus, setNewStatus] = useState("PRESENT");
  const [busy, setBusy] = useState(false);

  const sessions = useQuery({
    queryKey: ["admin-attendance", sectionId],
    enabled: Boolean(sectionId),
    queryFn: () => pages<Session>(`/api/v1/attendance/sessions?section_id=${encodeURIComponent(sectionId)}`)
  });

  const records = useQuery({
    queryKey: ["admin-attendance-records", selectedId],
    enabled: Boolean(selectedId),
    queryFn: () => pages<RecordRow>(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/records`)
  });

  const history = useQuery({
    queryKey: ["admin-attendance-history", selectedId],
    enabled: Boolean(selectedId),
    queryFn: () => pages<ChangeRow>(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/history`)
  });

  async function act(endpoint: string, method: "POST" | "PATCH", body?: object) {
    try {
      setBusy(true);
      await apiRequest(endpoint, { method, ...(body ? { body: JSON.stringify(body) } : {}) });
      await queryClient.invalidateQueries({ queryKey: ["admin-attendance"] });
      toast.push("Attendance operation saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Attendance operation failed.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Admin"
        title="Attendance Management"
        description="Review complete session records across sections, manage finalized sessions, and inspect attributable correction history."
      />

      <Card title="Select Academic Section">
        <label className="block text-sm font-medium">
          Section
          <select
            className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
            value={sectionId}
            onChange={(e) => {
              setSectionId(e.target.value);
              setSelectedId("");
            }}
          >
            <option value="">Select section</option>
            {(sections.data ?? []).map((section) => (
              <option key={section.id} value={section.id}>
                {section.name}
              </option>
            ))}
          </select>
        </label>

        {sections.error && <InlineError message="Academic sections could not be loaded." />}
        {sessions.error && <InlineError message="Attendance sessions could not be loaded." />}
        {sessions.isLoading && <SectionLoader label="Loading sessions…" />}

        {sectionId && sessions.data && (
          <div className="mt-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted mb-3">
              Attendance Sessions ({sessions.data.length})
            </h4>
            {sessions.data.length === 0 ? (
              <p className="text-sm text-muted">No attendance sessions recorded for this section.</p>
            ) : (
              <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
                {sessions.data.map((session) => (
                  <button
                    key={session.id}
                    type="button"
                    onClick={() => {
                      setSelectedId(session.id);
                      setStudentId("");
                    }}
                    className={`flex items-center justify-between rounded-xl border p-3 text-left transition ${
                      selectedId === session.id
                        ? "border-primary bg-primary-soft/60 font-semibold"
                        : "border-line bg-panel hover:bg-surface"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Calendar size={16} className="text-muted" />
                      <span className="text-sm">{session.session_date}</span>
                    </div>
                    <Badge>{session.status}</Badge>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>

      {selectedId && (
        <div className="space-y-6">
          <Card title="Session Lifecycle Actions">
            <Input
              label="Mandatory Audit Reason"
              placeholder="e.g. Approved faculty correction per department memo"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <Button
                disabled={busy || !reason.trim()}
                onClick={() => void act(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/reopen`, "POST", { reason })}
              >
                Reopen Session
              </Button>
              <Button
                variant="danger"
                disabled={busy || !reason.trim()}
                onClick={() => void act(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/cancel`, "POST", { reason })}
              >
                Cancel Session
              </Button>
            </div>
          </Card>

          <Card title="Attendance Records & Audited Corrections">
            {records.isLoading && <SectionLoader label="Loading records…" />}
            {records.error && <InlineError message="Attendance records could not be loaded." />}

            {records.data && (
              <div className="overflow-x-auto">
                <table className="min-w-[650px] w-full text-sm text-left">
                  <thead>
                    <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                      <th className="px-3 py-3">Student Identifier</th>
                      <th className="px-3 py-3">Marked Status</th>
                      <th className="px-3 py-3">Notes</th>
                      <th className="px-3 py-3 text-right">Audited Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.data.map((row) => (
                      <tr key={row.student_user_id} className="border-b border-line/60">
                        <td className="px-3 py-3 font-mono text-xs flex items-center gap-2">
                          <User size={14} className="text-muted" />
                          <span>{row.student_user_id}</span>
                        </td>
                        <td className="px-3 py-3">{statusBadge(row.status)}</td>
                        <td className="px-3 py-3 text-xs text-muted">{row.notes || "—"}</td>
                        <td className="px-3 py-3 text-right">
                          <Button
                            variant="secondary"
                            onClick={() => {
                              setStudentId(row.student_user_id);
                              setNewStatus(row.status);
                            }}
                          >
                            Correct
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {studentId && (
              <div className="mt-5 rounded-xl border border-primary/30 bg-primary-soft/45 p-4 space-y-3">
                <p className="text-sm font-semibold text-primary-ink">
                  Correcting Record: <span className="font-mono text-xs">{studentId}</span>
                </p>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block text-sm font-medium">
                    New Status
                    <select
                      aria-label="New attendance status"
                      className="mt-1 w-full rounded-xl border border-line bg-panel p-2.5 text-sm"
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value)}
                    >
                      {["PRESENT", "ABSENT", "LATE", "EXCUSED"].map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </label>
                  <Input
                    label="Correction Reason"
                    placeholder="Enter auditable justification"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </div>
                <Button
                  disabled={busy || !reason.trim()}
                  onClick={() =>
                    void act(
                      `/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/records/${encodeURIComponent(studentId)}`,
                      "PATCH",
                      { status: newStatus, reason }
                    )
                  }
                >
                  Save Audited Correction
                </Button>
              </div>
            )}
          </Card>

          <Card title="Session Audit History">
            {history.isLoading && <SectionLoader label="Loading history…" />}
            {history.error && <InlineError message="History could not be loaded." />}
            {history.data && (
              <ul className="space-y-2.5 text-sm">
                {history.data.length === 0 ? (
                  <p className="text-sm text-muted">No audit modifications recorded for this session.</p>
                ) : (
                  history.data.map((entry, index) => (
                    <li key={index} className="flex items-start gap-3 border-b border-line pb-2.5">
                      <History size={16} className="text-brand-600 mt-0.5 shrink-0" />
                      <div>
                        <p className="font-semibold text-xs uppercase tracking-wide text-brand-700">
                          {entry.action || "Audit Event"}
                        </p>
                        <p className="text-sm mt-0.5">{entry.reason}</p>
                        <p className="text-xs text-muted mt-1">
                          {entry.changed_at ? new Date(entry.changed_at).toLocaleString() : ""} · Actor: {entry.changed_by_user_id || "System"}
                        </p>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
