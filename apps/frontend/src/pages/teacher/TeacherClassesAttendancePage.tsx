import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useAttendanceSessions,
  useCreateAttendanceSession,
  useFinalizeAttendanceSession,
  useSaveBulkAttendance,
  useSectionRoster,
  useSessionAttendance,
  useTeacherSections
} from "../../features/teacher/hooks";
import { correctAttendanceRecord } from "../../features/teacher/teacher-api";
import type { AttendanceEntry } from "../../features/teacher/types";

const statuses: AttendanceEntry["status"][] = [
  "PRESENT",
  "ABSENT",
  "LATE",
  "EXCUSED"
];

export function TeacherClassesAttendancePage() {
  const toast = useToast();
  const sections = useTeacherSections();
  const [sectionId, setSectionId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [sessionDate, setSessionDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [entries, setEntries] = useState<AttendanceEntry[]>([]);
  const [correctionReasons, setCorrectionReasons] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!sectionId && sections.data?.[0]) {
      setSectionId(sections.data[0].id);
    }
  }, [sectionId, sections.data]);

  const roster = useSectionRoster(sectionId);
  const sessions = useAttendanceSessions(sectionId);
  const sessionAttendance = useSessionAttendance(sessionId);
  const createSession = useCreateAttendanceSession();
  const saveBulk = useSaveBulkAttendance();
  const finalize = useFinalizeAttendanceSession();

  useEffect(() => {
    if (sessionAttendance.data?.length) {
      setEntries(sessionAttendance.data);
      return;
    }

    if (roster.data?.length && sessionId) {
      setEntries(
        roster.data.map((member) => ({
          studentUserId: member.userId,
          studentName: member.name ?? member.studentId ?? member.userId,
          status: "PRESENT",
          notes: null
        }))
      );
    }
  }, [sessionAttendance.data, roster.data, sessionId]);

  const selectedSection = useMemo(
    () => sections.data?.find((section) => section.id === sectionId),
    [sectionId, sections.data]
  );

  if (sections.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading assigned classes…" />
      </div>
    );
  }

  if (sections.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Classes & attendance" />
        <InlineError message="Your assigned sections could not be loaded." />
      </div>
    );
  }

  const createNewSession = async (event: FormEvent) => {
    event.preventDefault();

    if (!sectionId || !sessionDate) {
      toast.push("Select a section and date.", "error");
      return;
    }

    try {
      const created = await createSession.mutateAsync({
        section_id: sectionId,
        session_date: sessionDate,
        starts_at: startsAt || undefined,
        ends_at: endsAt || undefined
      });
      setSessionId(created.id);
      toast.push("Attendance session created.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not create attendance session.",
        "error"
      );
    }
  };

  const updateEntry = (
    studentUserId: string,
    patch: Partial<AttendanceEntry>
  ) => {
    setEntries((current) =>
      current.map((entry) =>
        entry.studentUserId === studentUserId ? { ...entry, ...patch } : entry
      )
    );
  };

  const save = async () => {
    if (!sessionId) return;
    try {
      await saveBulk.mutateAsync({ sessionId, records: entries });
      toast.push("Attendance saved.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not save attendance.",
        "error"
      );
    }
  };

  const finalizeSession = async () => {
    if (!sessionId) return;
    try {
      await finalize.mutateAsync(sessionId);
      toast.push("Attendance session finalized.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not finalize attendance.",
        "error"
      );
    }
  };

  const correct = async (entry: AttendanceEntry) => {
    if (!entry.id) {
      toast.push("Save attendance before applying a correction.", "error");
      return;
    }
    const reason = correctionReasons[entry.id]?.trim();
    if (!reason) {
      toast.push("Enter a correction reason.", "error");
      return;
    }

    try {
      const updated = await correctAttendanceRecord(sessionId, entry.studentUserId, {
        status: entry.status,
        notes: entry.notes,
        reason
      });
      setEntries((current) =>
        current.map((item) => (item.id === entry.id ? updated : item))
      );
      setCorrectionReasons((current) => ({ ...current, [entry.id!]: "" }));
      toast.push("Attendance correction recorded.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Correction failed.",
        "error"
      );
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Classes & attendance"
        description="Open assigned sections, review rosters, create attendance sessions, bulk mark students, finalize sheets, and record corrections."
      />

      {!sections.data?.length ? (
        <Card>
          <p className="text-sm text-muted">No academic sections are currently assigned to you.</p>
        </Card>
      ) : (
        <>
          <Card title="Assigned class">
            <label className="block text-sm font-medium">
              Section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={sectionId}
                onChange={(event) => {
                  setSectionId(event.target.value);
                  setSessionId("");
                  setEntries([]);
                }}
              >
                {sections.data.map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.courseCode ? `${section.courseCode} · ` : ""}
                    {section.name}
                    {section.courseTitle ? ` · ${section.courseTitle}` : ""}
                  </option>
                ))}
              </select>
            </label>

            {selectedSection ? (
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted">Course</p>
                  <p className="mt-1 text-sm font-semibold">
                    {selectedSection.courseTitle ??
                      selectedSection.courseCode ??
                      selectedSection.courseId ??
                      "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted">Section</p>
                  <p className="mt-1 text-sm font-semibold">{selectedSection.name}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted">Capacity</p>
                  <p className="mt-1 text-sm font-semibold">
                    {selectedSection.capacity ?? "—"}
                  </p>
                </div>
              </div>
            ) : null}
          </Card>

          <div className="mt-6 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
            <Card title="Roster">
              {roster.isLoading ? (
                <SectionLoader label="Loading roster…" />
              ) : roster.error ? (
                <InlineError message="The section roster could not be loaded." />
              ) : roster.data?.length ? (
                <div className="max-h-[34rem] overflow-auto">
                  <table className="w-full min-w-[440px] text-left text-sm">
                    <thead>
                      <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                        <th className="px-2 py-3">Student</th>
                        <th className="px-2 py-3">Student ID</th>
                        <th className="px-2 py-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {roster.data.map((member) => (
                        <tr key={member.userId} className="border-b border-line/70">
                          <td className="px-2 py-3">
                            <p className="font-medium">
                              {member.name ?? member.email ?? member.userId}
                            </p>
                            {member.email ? (
                              <p className="mt-1 text-xs text-muted">{member.email}</p>
                            ) : null}
                          </td>
                          <td className="px-2 py-3">{member.studentId ?? "—"}</td>
                          <td className="px-2 py-3">
                            <Badge>{member.enrollmentStatus ?? "ACTIVE"}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-sm text-muted">No enrolled students are visible in this section.</p>
              )}
            </Card>

            <Card title="Attendance sessions">
              <form
                className="grid gap-3 sm:grid-cols-2"
                onSubmit={(event) => void createNewSession(event)}
              >
                <Input
                  label="Session date"
                  type="date"
                  value={sessionDate}
                  onChange={(event) => setSessionDate(event.target.value)}
                />
                <div className="hidden sm:block" />
                <Input
                  label="Starts at"
                  type="time"
                  value={startsAt}
                  onChange={(event) => setStartsAt(event.target.value)}
                />
                <Input
                  label="Ends at"
                  type="time"
                  value={endsAt}
                  onChange={(event) => setEndsAt(event.target.value)}
                />
                <Button type="submit" disabled={createSession.isPending}>
                  {createSession.isPending ? "Creating…" : "Create session"}
                </Button>
              </form>

              <div className="mt-6">
                <label className="block text-sm font-medium">
                  Existing session
                  <select
                    className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                    value={sessionId}
                    onChange={(event) => setSessionId(event.target.value)}
                  >
                    <option value="">Select a session</option>
                    {(sessions.data ?? []).map((session) => (
                      <option key={session.id} value={session.id}>
                        {session.sessionDate} · {session.status}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </Card>
          </div>

          {sessionId ? (
            <Card className="mt-6" title="Attendance sheet">
              {sessionAttendance.isLoading ? (
                <SectionLoader label="Loading attendance sheet…" />
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[900px] text-left text-sm">
                      <thead>
                        <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                          <th className="px-2 py-3">Student</th>
                          <th className="px-2 py-3">Status</th>
                          <th className="px-2 py-3">Notes</th>
                          <th className="px-2 py-3">Correction reason</th>
                          <th className="px-2 py-3">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {entries.map((entry) => (
                          <tr
                            key={entry.studentUserId}
                            className="border-b border-line/70 align-top"
                          >
                            <td className="px-2 py-3 font-medium">
                              {entry.studentName ?? entry.studentUserId}
                            </td>
                            <td className="px-2 py-3">
                              <select
                                className="rounded-lg border border-line bg-panel px-2 py-2"
                                value={entry.status}
                                onChange={(event) =>
                                  updateEntry(entry.studentUserId, {
                                    status: event.target.value as AttendanceEntry["status"]
                                  })
                                }
                              >
                                {statuses.map((status) => (
                                  <option key={status} value={status}>
                                    {status}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="px-2 py-3">
                              <input
                                className="w-full rounded-lg border border-line px-2 py-2"
                                value={entry.notes ?? ""}
                                onChange={(event) =>
                                  updateEntry(entry.studentUserId, {
                                    notes: event.target.value
                                  })
                                }
                              />
                            </td>
                            <td className="px-2 py-3">
                              <input
                                className="w-full rounded-lg border border-line px-2 py-2"
                                placeholder="Required for corrections"
                                value={entry.id ? correctionReasons[entry.id] ?? "" : ""}
                                disabled={!entry.id}
                                onChange={(event) =>
                                  entry.id &&
                                  setCorrectionReasons((current) => ({
                                    ...current,
                                    [entry.id!]: event.target.value
                                  }))
                                }
                              />
                            </td>
                            <td className="px-2 py-3">
                              <Button
                                variant="secondary"
                                disabled={!entry.id}
                                onClick={() => void correct(entry)}
                              >
                                Correct
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-5 flex flex-wrap justify-end gap-3">
                    <Button
                      variant="secondary"
                      onClick={() => void save()}
                      disabled={saveBulk.isPending || !entries.length}
                    >
                      {saveBulk.isPending ? "Saving…" : "Save attendance"}
                    </Button>
                    <Button
                      onClick={() => void finalizeSession()}
                      disabled={finalize.isPending}
                    >
                      {finalize.isPending ? "Finalizing…" : "Finalize session"}
                    </Button>
                  </div>
                </>
              )}
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}
