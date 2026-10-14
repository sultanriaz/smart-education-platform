import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { useToast } from "../../components/ui/useToast";
import { apiRequest } from "../../lib/api-client";
import { useSections } from "../../features/admin/hooks";

interface Session {
  id: string; section_id: string; session_date: string; status: string;
}
interface RecordRow { student_user_id: string; status: string; notes: string | null; }
interface ChangeRow { action?: string; reason?: string; changed_at?: string; changed_by_user_id?: string; }
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
  const sessions = useQuery({ queryKey: ["admin-attendance", sectionId], enabled: Boolean(sectionId), queryFn: () => pages<Session>(`/api/v1/attendance/sessions?section_id=${encodeURIComponent(sectionId)}`) });
  const records = useQuery({ queryKey: ["admin-attendance-records", selectedId], enabled: Boolean(selectedId), queryFn: () => pages<RecordRow>(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/records`) });
  const history = useQuery({ queryKey: ["admin-attendance-history", selectedId], enabled: Boolean(selectedId), queryFn: () => pages<ChangeRow>(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/history`) });
  async function act(endpoint: string, method: "POST" | "PATCH", body?: object) {
    try {
      setBusy(true);
      await apiRequest(endpoint, { method, ...(body ? { body: JSON.stringify(body) } : {}) });
      await queryClient.invalidateQueries({ queryKey: ["admin-attendance"] });
      toast.push("Attendance operation saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Attendance operation failed.", "error");
    } finally { setBusy(false); }
  }
  return <div className="page-container space-y-6">
    <PageHeader eyebrow="Admin" title="Attendance management" description="Review complete session records, manage finalized sessions, and inspect attributable change history." />
    <Card title="Select academic section">
      <label className="block text-sm">Section
        <select className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5" value={sectionId} onChange={e => { setSectionId(e.target.value); setSelectedId(""); }}>
          <option value="">Select section</option>{(sections.data ?? []).map(section => <option key={section.id} value={section.id}>{section.name}</option>)}
        </select>
      </label>
      {sections.error && <p role="alert">Academic sections could not be loaded.</p>}
      {sessions.error && <p role="alert">Attendance sessions could not be loaded.</p>}
      {sessions.isLoading && <p>Loading sessions…</p>}
      <ul className="mt-4 space-y-2">{(sessions.data ?? []).map(session => <li key={session.id}><Button variant="secondary" onClick={() => { setSelectedId(session.id); setStudentId(""); }} aria-pressed={selectedId === session.id}>{session.session_date} · {session.status}</Button></li>)}</ul>
    </Card>
    {selectedId && <><Card title="Session lifecycle">
      <Input label="Required reason" value={reason} onChange={e => setReason(e.target.value)} />
      <div className="mt-3 flex flex-wrap gap-2"><Button disabled={busy || !reason.trim()} onClick={() => void act(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/reopen`, "POST", { reason })}>Reopen</Button>
        <Button variant="danger" disabled={busy || !reason.trim()} onClick={() => void act(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/cancel`, "POST", { reason })}>Cancel</Button>
      </div></Card>
      <Card title="Attendance records and audited corrections">
        {records.isLoading && <p>Loading records…</p>}{records.error && <p role="alert">Attendance records could not be loaded.</p>}
        <div className="overflow-x-auto"><table className="min-w-[580px] w-full text-sm"><thead><tr><th>Student</th><th>Status</th><th>Action</th></tr></thead><tbody>{(records.data ?? []).map(row => <tr key={row.student_user_id}><td className="p-2 font-mono text-xs">{row.student_user_id}</td><td>{row.status}</td><td><Button variant="secondary" onClick={() => { setStudentId(row.student_user_id); setNewStatus(row.status); }}>Correct</Button></td></tr>)}</tbody></table></div>
        {studentId && <div className="mt-4 space-y-3"><p className="text-xs">Correcting {studentId}</p><select aria-label="New attendance status" className="w-full rounded-xl border border-line bg-panel p-3" value={newStatus} onChange={e => setNewStatus(e.target.value)}>{["PRESENT", "ABSENT", "LATE", "EXCUSED"].map(status => <option key={status} value={status}>{status}</option>)}</select><Input label="Correction reason" value={reason} onChange={e => setReason(e.target.value)} /><Button disabled={busy || !reason.trim()} onClick={() => void act(`/api/v1/attendance/sessions/${encodeURIComponent(selectedId)}/records/${encodeURIComponent(studentId)}`, "PATCH", { status: newStatus, reason })}>Save correction</Button></div>}
      </Card>
      <Card title="Session audit history">{history.isLoading && <p>Loading history…</p>}{history.error && <p role="alert">History could not be loaded.</p>}<ul className="space-y-2 text-sm">{(history.data ?? []).map((entry, index) => <li className="border-b border-line pb-2" key={index}>{entry.action} · {entry.reason} · {entry.changed_at} · {entry.changed_by_user_id}</li>)}</ul></Card>
    </>}
  </div>;
}
