import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Calendar, Clock, Users } from "lucide-react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import { InteractiveClassRosterSheet } from "../../components/teacher/InteractiveClassRosterSheet";
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
import {
  FACULTY_CLASSES,
  FACULTY_TIME_SLOTS,
  loadSavedAttendanceSheets,
  type SavedAttendanceSheet
} from "../../features/teacher/teacher-portal-data";
import type { AttendanceEntry } from "../../features/teacher/types";

const statuses: AttendanceEntry["status"][] = [
  "PRESENT",
  "ABSENT",
  "LATE",
  "EXCUSED"
];

export function TeacherClassesAttendancePage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const sections = useTeacherSections();

  const initialClassParam = searchParams.get("class") ?? "";
  const initialSlotParam = searchParams.get("slot") ?? "Slot 2";
  const isTakeMode = searchParams.get("mode") === "take";

  const [selectedFacultyClassId, setSelectedFacultyClassId] = useState<string>(
    FACULTY_CLASSES.some((c) => c.id === initialClassParam)
      ? initialClassParam
      : FACULTY_CLASSES[0]!.id
  );
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().slice(0, 10)
  );
  const [selectedSlot, setSelectedSlot] = useState<string>(
    FACULTY_TIME_SLOTS.some((s) => s.slot === initialSlotParam)
      ? initialSlotParam
      : FACULTY_TIME_SLOTS[1]!.slot
  );
  const [sheetActive, setSheetActive] = useState<boolean>(true);
  const [savedSheets, setSavedSheets] = useState<Record<string, SavedAttendanceSheet>>(() =>
    loadSavedAttendanceSheets()
  );

  const [sectionId, setSectionId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [scheduleOccurrenceId, setScheduleOccurrenceId] = useState("");
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
    if (!sessionId || !roster.data || !sessionAttendance.data) {
      setEntries([]);
      return;
    }
    const marked = new Map(
      sessionAttendance.data.map((entry) => [entry.studentUserId, entry])
    );
    setEntries(
      roster.data.map((member) => ({
        studentUserId: member.userId,
        studentName: member.name ?? member.studentId ?? member.userId,
        status: "PRESENT" as AttendanceEntry["status"],
        notes: null,
        ...(marked.get(member.userId) ?? {})
      }))
    );
  }, [sessionAttendance.data, roster.data, sessionId]);

  const selectedSection = useMemo(
    () => sections.data?.find((section) => section.id === sectionId),
    [sectionId, sections.data]
  );

  const activeFacultyClass = useMemo(
    () =>
      FACULTY_CLASSES.find((c) => c.id === selectedFacultyClassId) ??
      FACULTY_CLASSES[0]!,
    [selectedFacultyClassId]
  );

  if (sections.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading assigned classes…" />
      </div>
    );
  }

  const hasApiSections = Boolean(sections.data?.length);
  const activeSheetKey = `${activeFacultyClass.id}__${selectedDate}__${selectedSlot}`;
  const activeSavedSheet = savedSheets[activeSheetKey];

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
        schedule_occurrence_id: scheduleOccurrenceId.trim() || undefined,
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
      await queryClient.invalidateQueries({ queryKey: ["teacher", "attendance", "session", sessionId] });
      setCorrectionReasons((current) => ({ ...current, [entry.id!]: "" }));
      toast.push("Attendance correction recorded.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Correction failed.",
        "error"
      );
    }
  };

  const markAllWithStatus = (newStatus: AttendanceEntry["status"]) => {
    setEntries((prev) => prev.map((e) => ({ ...e, status: newStatus })));
    toast.push(`Marked all students as ${newStatus}.`, "success");
  };

  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Teacher"
        title={isTakeMode ? "Take Class Attendance" : "Classes & attendance"}
        description="Select a class, date, and lecture slot to mark Present or Absent across the enrolled student roster, submit, or edit."
      />

      {sections.error ? (
        <InlineError
          message="Live section sync was unavailable; local faculty classes remain active."
          onRetry={() => void sections.refetch()}
          isRetrying={sections.isFetching}
        />
      ) : null}

      {/* Enrolled Classes Grid */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted">
          Your Enrolled Classes
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {FACULTY_CLASSES.map((cls) => {
            const isSelected = cls.id === activeFacultyClass.id;
            return (
              <button
                key={cls.id}
                type="button"
                aria-pressed={isSelected}
                onClick={() => {
                  setSelectedFacultyClassId(cls.id);
                  setSheetActive(true);
                }}
                className={`rounded-2xl border p-4 text-left transition cursor-pointer ${
                  isSelected
                    ? "border-primary bg-primary-soft/35 shadow-xs"
                    : "border-line bg-panel hover:border-primary/50"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-bold text-primary-ink">
                    {cls.courseCode}
                  </span>
                  <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-xs font-bold text-ink">
                    {cls.section}
                  </span>
                </div>
                <p className="mt-1.5 font-bold text-sm text-ink">{cls.courseTitle}</p>
                <p className="mt-1 text-xs text-muted">{cls.scheduleSummary}</p>
                <div className="mt-2.5 inline-flex items-center gap-1 text-xs font-semibold text-primary-ink">
                  <Users size={13} />
                  <span>{cls.students.length} Students on Roster</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Day & Slot Controls */}
      <Card
        title={isTakeMode ? "Select Date & Time Slot" : "Session Date & Lecture Slot"}
        description="Choose the session date and slot to take or edit attendance for the selected class."
      >
        <div className="grid gap-4 sm:grid-cols-3 items-end">
          <label className="block text-xs font-bold text-ink">
            <span className="mb-1.5 flex items-center gap-1.5 text-muted">
              <Calendar size={13} className="text-primary-ink" />
              <span>Date</span>
            </span>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => {
                setSelectedDate(e.target.value);
                setSheetActive(true);
              }}
              className="w-full min-h-11 rounded-xl border border-line bg-surface px-3 py-2 text-sm sm:text-xs font-semibold text-ink"
            />
          </label>

          <label className="block text-xs font-bold text-ink">
            <span className="mb-1.5 flex items-center gap-1.5 text-muted">
              <Clock size={13} className="text-primary-ink" />
              <span>Time Slot</span>
            </span>
            <select
              value={selectedSlot}
              onChange={(e) => {
                setSelectedSlot(e.target.value);
                setSheetActive(true);
              }}
              className="w-full min-h-11 rounded-xl border border-line bg-surface px-3 py-2 text-sm sm:text-xs font-semibold text-ink"
            >
              {FACULTY_TIME_SLOTS.map((opt) => (
                <option key={opt.slot} value={opt.slot}>
                  {opt.slot} ({opt.timeRange})
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={() => setSheetActive(true)}
            className="min-h-11 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary shadow-xs hover:bg-primary-hover transition cursor-pointer"
          >
            {activeSavedSheet ? "Open Saved Sheet" : "Take Attendance"}
          </button>
        </div>
      </Card>

      {/* Interactive Student Roster & Attendance Sheet */}
      {sheetActive && (
        <InteractiveClassRosterSheet
          classInfo={activeFacultyClass}
          date={selectedDate}
          slot={selectedSlot}
          savedSheet={activeSavedSheet}
          onSubmitted={(sheet) => {
            setSavedSheets((prev) => ({ ...prev, [sheet.key]: sheet }));
            toast.push(`Attendance submitted for ${activeFacultyClass.section}.`, "success");
          }}
        />
      )}

      {!hasApiSections ? null : (
        <div className="space-y-6 pt-2">
          <Card title="Synced Server Section">
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
                {sections.data!.map((section) => (
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

          <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
            <Card title="Server Roster">
              {roster.isLoading ? (
                <SectionLoader label="Loading roster…" />
              ) : roster.error ? (
                <InlineError
                  message="The section roster could not be loaded."
                  onRetry={() => void roster.refetch()}
                  isRetrying={roster.isFetching}
                />
              ) : roster.data?.length ? (
                <div className="max-h-[34rem] overflow-auto focus-visible:outline-2 focus-visible:outline-offset-2" role="region" aria-label="Student roster" tabIndex={0}>
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
                <Input label="Scheduling occurrence UUID (optional)" hint="Link the session to a published timetable occurrence; the server validates the owner/date." value={scheduleOccurrenceId} onChange={e => setScheduleOccurrenceId(e.target.value)} />
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
            <Card className="mt-6" title="Server Attendance sheet">
              {sessionAttendance.isLoading ? (
                <SectionLoader label="Loading attendance sheet…" />
              ) : (
                <>
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
                    <div className="flex items-center gap-2">
                      <Button variant="secondary" onClick={() => markAllWithStatus("PRESENT")}>
                        ✓ Mark All Present
                      </Button>
                      <Button variant="secondary" onClick={() => markAllWithStatus("ABSENT")}>
                        ✗ Mark All Absent
                      </Button>
                    </div>
                    <span className="text-xs text-muted">
                      {entries.length} students loaded on roster
                    </span>
                  </div>

                  <div className="overflow-x-auto focus-visible:outline-2 focus-visible:outline-offset-2" role="region" aria-label="Attendance sheet" tabIndex={0}>
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
        </div>
      )}
    </div>
  );
}
