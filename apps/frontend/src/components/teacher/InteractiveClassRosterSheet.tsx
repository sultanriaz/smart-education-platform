import { useEffect, useMemo, useState } from "react";
import { Check, Edit3, Users, X } from "lucide-react";
import {
  saveAttendanceSheet,
  type BinaryAttendanceStatus,
  type FacultyClassInfo,
  type SavedAttendanceSheet
} from "../../features/teacher/teacher-portal-data";

interface Props {
  classInfo: FacultyClassInfo;
  date: string;
  slot: string;
  savedSheet?: SavedAttendanceSheet;
  onSubmitted?: (sheet: SavedAttendanceSheet) => void;
  onClose?: () => void;
}

/** Interactive class attendance sheet showing student names, roll numbers, Present/Absent toggles, Edit, and Submit. */
export function InteractiveClassRosterSheet({
  classInfo,
  date,
  slot,
  savedSheet,
  onSubmitted,
  onClose
}: Props) {
  const buildDefaultMap = (existing?: SavedAttendanceSheet) => {
    const map: Record<string, BinaryAttendanceStatus> = {};
    for (const stu of classInfo.students) {
      map[stu.studentId] = existing?.records[stu.studentId] ?? "PRESENT";
    }
    return map;
  };

  const [records, setRecords] = useState<Record<string, BinaryAttendanceStatus>>(() =>
    buildDefaultMap(savedSheet)
  );
  const [isSubmitted, setIsSubmitted] = useState<boolean>(Boolean(savedSheet));
  const [isEditing, setIsEditing] = useState<boolean>(!savedSheet);
  const [statusNotice, setStatusNotice] = useState<string | null>(null);

  const sheetKey = `${classInfo.id}__${date}__${slot}`;

  useEffect(() => {
    setRecords(buildDefaultMap(savedSheet));
    setIsSubmitted(Boolean(savedSheet));
    setIsEditing(!savedSheet);
    setStatusNotice(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sheetKey, savedSheet?.submittedAt]);

  const counts = useMemo(() => {
    let present = 0;
    let absent = 0;
    for (const stu of classInfo.students) {
      if (records[stu.studentId] === "ABSENT") absent += 1;
      else present += 1;
    }
    return { present, absent, total: classInfo.students.length };
  }, [classInfo.students, records]);

  const setStudentStatus = (studentId: string, status: BinaryAttendanceStatus) => {
    if (!isEditing) return;
    setRecords((prev) => ({ ...prev, [studentId]: status }));
  };

  const markAll = (status: BinaryAttendanceStatus) => {
    if (!isEditing) return;
    const next: Record<string, BinaryAttendanceStatus> = {};
    for (const stu of classInfo.students) {
      next[stu.studentId] = status;
    }
    setRecords(next);
  };

  const handleSubmit = () => {
    const sheet: SavedAttendanceSheet = {
      key: sheetKey,
      classId: classInfo.id,
      date,
      slot,
      submittedAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      records
    };
    saveAttendanceSheet(sheet);
    setIsSubmitted(true);
    setIsEditing(false);
    setStatusNotice(`Attendance submitted (${counts.present} Present, ${counts.absent} Absent).`);
    onSubmitted?.(sheet);
  };

  return (
    <div className="rounded-2xl border border-line bg-panel p-4 sm:p-5 space-y-4 shadow-xs">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs font-bold text-primary-ink">
              {classInfo.courseCode}
            </span>
            <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-xs font-bold text-ink">
              {classInfo.section}
            </span>
            <span className="rounded-md bg-primary-soft px-2 py-0.5 text-xs font-semibold text-primary-ink">
              {date} · {slot}
            </span>
          </div>
          <h3 className="mt-1 text-base font-bold text-ink">{classInfo.courseTitle} — Attendance Sheet</h3>
          <p className="text-xs text-muted mt-0.5">{classInfo.room}</p>
        </div>

        <div className="flex items-center gap-2">
          {isSubmitted && !isEditing && (
            <button
              type="button"
              onClick={() => {
                setIsEditing(true);
                setStatusNotice(null);
              }}
              className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer"
            >
              <Edit3 size={14} />
              <span>Edit</span>
            </button>
          )}
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              aria-label="Close attendance sheet"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-line bg-surface text-muted hover:text-ink transition cursor-pointer"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Live summary & bulk controls */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-surface border border-line px-2.5 py-1.5 font-semibold text-ink">
            <Users size={13} className="text-primary-ink" />
            <span>{counts.total} Students</span>
          </span>
          <span className="rounded-lg bg-success-soft px-2.5 py-1.5 font-bold text-success-ink">
            Present: {counts.present}
          </span>
          <span className="rounded-lg bg-danger-soft px-2.5 py-1.5 font-bold text-danger-ink">
            Absent: {counts.absent}
          </span>
        </div>

        {isEditing && (
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => markAll("PRESENT")}
              className="min-h-10 rounded-xl border border-success/40 bg-success-soft px-3 py-1.5 text-xs font-bold text-success-ink hover:opacity-90 transition cursor-pointer"
            >
              Mark All Present
            </button>
            <button
              type="button"
              onClick={() => markAll("ABSENT")}
              className="min-h-10 rounded-xl border border-danger/40 bg-danger-soft px-3 py-1.5 text-xs font-bold text-danger-ink hover:opacity-90 transition cursor-pointer"
            >
              Mark All Absent
            </button>
          </div>
        )}
      </div>

      {statusNotice && (
        <div
          role="status"
          className="rounded-xl border border-success/40 bg-success-soft px-3.5 py-2.5 text-xs font-semibold text-success-ink"
        >
          {statusNotice}
        </div>
      )}

      {/* Student Roster Rows */}
      <div className="overflow-x-auto rounded-2xl border border-line">
        <table className="w-full text-left text-xs sm:text-sm">
          <thead className="bg-surface text-[11px] font-bold uppercase tracking-wider text-muted">
            <tr>
              <th className="px-3 py-2.5">Roll No</th>
              <th className="px-3 py-2.5">Student Name</th>
              <th className="px-3 py-2.5 text-right">Attendance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line bg-panel">
            {classInfo.students.map((stu) => {
              const status = records[stu.studentId] ?? "PRESENT";
              return (
                <tr key={stu.studentId}>
                  <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs font-bold text-primary-ink">
                    {stu.rollNo}
                  </td>
                  <td className="px-3 py-2.5 font-semibold text-ink">{stu.name}</td>
                  <td className="px-3 py-2.5">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        type="button"
                        disabled={!isEditing}
                        aria-pressed={status === "PRESENT"}
                        onClick={() => setStudentStatus(stu.studentId, "PRESENT")}
                        className={`min-h-10 rounded-xl px-3 py-1.5 text-xs font-bold transition ${
                          status === "PRESENT"
                            ? "bg-success text-success-fg shadow-2xs"
                            : "border border-line bg-surface text-muted hover:text-ink"
                        } disabled:cursor-default disabled:opacity-85`}
                      >
                        Present
                      </button>
                      <button
                        type="button"
                        disabled={!isEditing}
                        aria-pressed={status === "ABSENT"}
                        onClick={() => setStudentStatus(stu.studentId, "ABSENT")}
                        className={`min-h-10 rounded-xl px-3 py-1.5 text-xs font-bold transition ${
                          status === "ABSENT"
                            ? "bg-danger text-danger-fg shadow-2xs"
                            : "border border-line bg-surface text-muted hover:text-ink"
                        } disabled:cursor-default disabled:opacity-85`}
                      >
                        Absent
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer Actions */}
      <div className="flex flex-wrap items-center justify-end gap-2 pt-1">
        {isEditing ? (
          <button
            type="button"
            onClick={handleSubmit}
            className="inline-flex min-h-11 items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-on-primary shadow-xs hover:bg-primary-hover transition cursor-pointer"
          >
            <Check size={15} />
            <span>Submit Attendance</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              setIsEditing(true);
              setStatusNotice(null);
            }}
            className="inline-flex min-h-11 items-center gap-1.5 rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer"
          >
            <Edit3 size={14} />
            <span>Edit Attendance</span>
          </button>
        )}
      </div>
    </div>
  );
}
