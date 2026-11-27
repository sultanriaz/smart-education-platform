import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  GraduationCap,
  Clock,
  MapPin,
  CheckCircle2,
  ClipboardCheck,
  ArrowUpRight,
  BookOpen,
  Bell,
  Compass,
  Building,
  Check,
  ChevronRight
} from "lucide-react";

import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { InteractiveClassRosterSheet } from "../../components/teacher/InteractiveClassRosterSheet";
import { FolderGradingSheet } from "../../components/teacher/FolderGradingSheet";
import { useUnreadCount } from "../../features/student/hooks";
import {
  useTeacherAssignments,
  useTeacherSections,
  useTeacherTimetable
} from "../../features/teacher/hooks";
import {
  FACULTY_CLASSES,
  loadFolderGrades,
  loadSavedAttendanceSheets,
  saveFolderGrades,
  type ClassAssessmentFolder,
  type SavedAttendanceSheet
} from "../../features/teacher/teacher-portal-data";

interface TodayLecture {
  id: string;
  classId: string;
  courseCode: string;
  courseTitle: string;
  section: string;
  slot: string;
  time: string;
  room: string;
  enrolledStudents: number;
}

const DEFAULT_TODAY_LECTURES: TodayLecture[] = [
  {
    id: "lec-1",
    classId: "cls-compiler-7c",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    section: "BCS-7C",
    slot: "Slot 2",
    time: "10:15 AM – 11:45 AM",
    room: "Room C-204 (C Block, 2nd Floor)",
    enrolledStudents: 10
  },
  {
    id: "lec-2",
    classId: "cls-compiler-7a",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction Lab",
    section: "BCS-7A",
    slot: "Slot 4",
    time: "02:00 PM – 03:30 PM",
    room: "Software Lab 2 (C Block, Ground Floor)",
    enrolledStudents: 8
  },
  {
    id: "lec-3",
    classId: "cls-ai-8b",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence",
    section: "BCS-8B",
    slot: "Slot 5",
    time: "03:45 PM – 05:15 PM",
    room: "Room A-201 (A Block, 2nd Floor)",
    enrolledStudents: 8
  }
];

export function TeacherDashboardPage() {
  const sections = useTeacherSections();
  const timetable = useTeacherTimetable();
  const assignments = useTeacherAssignments();
  const unread = useUnreadCount();

  const todayDate = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [savedSheets, setSavedSheets] = useState<Record<string, SavedAttendanceSheet>>(() =>
    loadSavedAttendanceSheets()
  );
  const [activeLectureRoster, setActiveLectureRoster] = useState<TodayLecture | null>(null);
  const [folders, setFolders] = useState<ClassAssessmentFolder[]>(() => loadFolderGrades());
  const [activeGradingFolderId, setActiveGradingFolderId] = useState<string | null>(null);

  if (
    sections.isLoading &&
    timetable.isLoading &&
    assignments.isLoading &&
    unread.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading faculty workspace…" />
      </div>
    );
  }

  const error =
    sections.error ?? timetable.error ?? assignments.error ?? unread.error;

  const pendingSubmissionCards = [
    {
      folderId: "cls-compiler-7c-as-1",
      title: "Compiler Construction: Assignment 1 (Flex)",
      subtitle: "Section BCS-7C"
    },
    {
      folderId: "cls-ai-8b-as-1",
      title: "Artificial Intelligence: Midterm Lab Project",
      subtitle: "Section BCS-8B"
    }
  ].map((card) => {
    const folder = folders.find((f) => f.id === card.folderId);
    const total = folder?.rows.length ?? 0;
    const ungraded = folder?.rows.filter((r) => r.marks === null).length ?? 0;
    return { ...card, folder, total, ungraded };
  });

  const totalPendingCount = pendingSubmissionCards.reduce((sum, item) => sum + item.ungraded, 0);
  const activeGradingFolder = folders.find((f) => f.id === activeGradingFolderId) ?? null;
  const activeGradingClass = activeGradingFolder
    ? FACULTY_CLASSES.find((c) => c.id === activeGradingFolder.classId)
    : undefined;

  const handleSaveFolderMarks = (updated: ClassAssessmentFolder) => {
    setFolders((prev) => {
      const next = prev.map((f) => (f.id === updated.id ? updated : f));
      saveFolderGrades(next);
      return next;
    });
  };

  return (
    <div className="page-container space-y-6">
      <DashboardWelcome
        subtitle="Dr. Munir Ahmad · Faculty of Computer Science. Manage your lecture timetable, class attendance, and evaluations."
        action="Take Class Attendance"
        to="/app/teacher/attendance?mode=take"
      />

      {error ? (
        <div className="mb-2">
          <InlineError
            message="Some live schedule feeds could not be synchronized. Local teaching schedule remains active."
            onRetry={() => {
              void sections.refetch();
              void timetable.refetch();
              void assignments.refetch();
              void unread.refetch();
            }}
            isRetrying={
              sections.isFetching ||
              timetable.isFetching ||
              assignments.isFetching ||
              unread.isFetching
            }
          />
        </div>
      ) : null}

      {/* Top Academic Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Today's Lectures"
          value={`${DEFAULT_TODAY_LECTURES.length} Lectures`}
          helper="Next: Compiler Construction (BCS-7C) at 10:15 AM."
        />
        <StatCard
          label="Assigned Sections"
          value={sections.data?.length ? `${sections.data.length} Sections` : "3 Sections"}
          helper="BCS-7C, BCS-7A, BCS-8B."
        />
        <StatCard
          label="Pending Grading"
          value={`${totalPendingCount} Submissions`}
          helper="Lexical Analysis Assignment 1."
        />
        <StatCard
          label="Campus Notifications"
          value={unread.data ?? "2"}
          helper="Departmental academic notices."
        />
      </div>

      {/* ================= 1. TODAY'S LECTURE SCHEDULE TIMELINE ================= */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-ink">Today's Lecture Schedule & Attendance Mark</h2>
            <p className="text-xs text-muted">
              Click "Take Attendance" or "Open Roster" to view student roll numbers and submit attendance.
            </p>
          </div>
          <Link
            to="/app/teacher/timetable"
            className="text-xs font-semibold text-brand-600 hover:underline hidden sm:inline-flex items-center gap-1"
          >
            <span>Weekly Timetable</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>

        <div className="space-y-3">
          {DEFAULT_TODAY_LECTURES.map((lec) => {
            const sheetKey = `${lec.classId}__${todayDate}__${lec.slot}`;
            const savedSheet = savedSheets[sheetKey];
            const isMarked = Boolean(savedSheet);
            const isSheetOpen = activeLectureRoster?.id === lec.id;
            const classInfo = FACULTY_CLASSES.find((c) => c.id === lec.classId) ?? FACULTY_CLASSES[0]!;

            return (
              <div key={lec.id} className="space-y-3">
                <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/60 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl font-bold font-mono text-xs shadow-xs ${
                        isMarked
                          ? "bg-success-soft text-success-ink border border-success/35"
                          : "bg-primary-soft text-primary-ink border border-primary/35"
                      }`}
                    >
                      {lec.slot}
                    </div>

                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs font-bold text-primary-ink">{lec.courseCode}</span>
                        <span className="rounded-md bg-surface px-2 py-0.5 text-xs font-semibold text-ink">
                          Section: {lec.section}
                        </span>
                        <span className="text-xs text-muted font-medium">({lec.enrolledStudents} Students)</span>
                        {isMarked ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-success-soft px-2 py-0.5 text-[11px] font-semibold text-success-ink">
                            <Check size={12} /> Attendance Taken
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-warning-soft px-2 py-0.5 text-[11px] font-semibold text-warning-ink">
                            <Clock size={12} /> Pending Submission
                          </span>
                        )}
                      </div>

                      <h3 className="font-bold text-base text-ink mt-1">{lec.courseTitle}</h3>

                      <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted">
                        <span className="flex items-center gap-1">
                          <Clock size={13} className="text-primary-ink" />
                          <span>{lec.time}</span>
                        </span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <MapPin size={13} className="text-primary-ink" />
                          <span>{lec.room}</span>
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 self-stretch md:self-auto justify-end">
                    <button
                      type="button"
                      onClick={() => setActiveLectureRoster(isSheetOpen ? null : lec)}
                      className={`min-h-10 rounded-xl px-3.5 py-2 text-xs font-semibold transition shadow-2xs cursor-pointer ${
                        isSheetOpen
                          ? "border border-primary bg-primary-soft text-primary-ink"
                          : isMarked
                          ? "border border-line bg-surface text-ink hover:border-primary"
                          : "bg-success text-success-fg hover:opacity-90"
                      }`}
                    >
                      {isSheetOpen ? "Hide Attendance" : isMarked ? "Edit Attendance" : "Take Attendance"}
                    </button>

                    <Link
                      to={`/app/teacher/attendance?class=${encodeURIComponent(lec.classId)}&slot=${encodeURIComponent(lec.slot)}`}
                      className="inline-flex min-h-10 items-center gap-1 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-on-primary hover:bg-primary-hover transition shadow-xs"
                    >
                      <span>Open Roster</span>
                      <ArrowUpRight size={14} />
                    </Link>
                  </div>
                </div>

                {isSheetOpen && (
                  <InteractiveClassRosterSheet
                    classInfo={classInfo}
                    date={todayDate}
                    slot={lec.slot}
                    savedSheet={savedSheet}
                    onSubmitted={(sheet) =>
                      setSavedSheets((prev) => ({ ...prev, [sheet.key]: sheet }))
                    }
                    onClose={() => setActiveLectureRoster(null)}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ================= 2. PENDING SUBMISSIONS & ROOM RESERVATION ================= */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pending Grading Card */}
        <Card title="Pending Assessment Submissions" description="Click any submission card to inspect student work and enter marks.">
          <div className="space-y-3 mt-2">
            {pendingSubmissionCards.map((item) => {
              const isOpen = activeGradingFolderId === item.folderId;
              return (
                <button
                  key={item.folderId}
                  type="button"
                  onClick={() => setActiveGradingFolderId(isOpen ? null : item.folderId)}
                  aria-expanded={isOpen}
                  className={`w-full text-left rounded-xl border p-4 flex items-center justify-between gap-3 transition cursor-pointer ${
                    isOpen
                      ? "border-primary bg-primary-soft/35"
                      : "border-line bg-surface/50 hover:border-primary/50"
                  }`}
                >
                  <div>
                    <p className="font-bold text-sm text-ink">{item.title}</p>
                    <p className="text-xs text-muted mt-0.5">
                      {item.subtitle} · {item.total} submitted
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`rounded-md px-2.5 py-1 text-xs font-bold ${
                        item.ungraded === 0
                          ? "bg-success-soft text-success-ink"
                          : "bg-warning-soft text-warning-ink"
                      }`}
                    >
                      {item.ungraded === 0 ? "All Graded" : `${item.ungraded} to Grade`}
                    </span>
                    <ChevronRight size={15} className="text-muted" />
                  </div>
                </button>
              );
            })}

            <Link
              to="/app/teacher/assessments"
              className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary-ink hover:underline"
            >
              <span>Manage all course assessments</span>
              <ArrowUpRight size={13} />
            </Link>
          </div>
        </Card>

        {/* Make-up Class & Single Faculty Reservation Card */}
        <Card title="Make-up Class & Room Reservation" description="Locate and reserve unoccupied classrooms or labs inside the Faculty Portal.">
          <div className="space-y-4 mt-2">
            <p className="text-xs text-muted leading-relaxed">
              Schedule a make-up lecture, seminar, or project viva using the interactive Faculty Space Finder and reservation ledger.
            </p>

            <Link
              to="/app/teacher/facilities"
              className="flex items-center justify-between rounded-2xl border border-primary/30 bg-primary-soft/35 p-4 hover:border-primary transition group"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary text-on-primary shadow-xs">
                  <Building size={20} />
                </span>
                <div>
                  <p className="text-sm font-bold text-ink group-hover:text-primary-ink transition">
                    Room &amp; Lab Reservation
                  </p>
                  <p className="text-xs text-muted mt-0.5">
                    Browse available slots across Blocks A–D &amp; reserve instantly
                  </p>
                </div>
              </div>
              <ArrowUpRight size={18} className="shrink-0 text-primary-ink" />
            </Link>
          </div>
        </Card>
      </div>

      {/* Inline Marks Entry Drawer when a Pending Assessment Submission is clicked */}
      {activeGradingFolder && (
        <FolderGradingSheet
          folder={activeGradingFolder}
          classInfo={activeGradingClass}
          onSaveFolder={handleSaveFolderMarks}
          onClose={() => setActiveGradingFolderId(null)}
        />
      )}

      {/* Quick Action Matrix */}
      <Card title="Faculty Modules & Services" description="Direct access to teaching tools and administrative services.">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 mt-3">
          {[
            { to: "/app/teacher/attendance", title: "Class Attendance", desc: "Digital attendance roster", icon: CheckCircle2 },
            { to: "/app/teacher/learning", title: "Lecture Resources", desc: "Upload slides & notes", icon: BookOpen },
            { to: "/app/teacher/assessments", title: "Quizzes & Grading", desc: "Create tests and evaluate", icon: ClipboardCheck },
            { to: "/app/teacher/announcements", title: "Announcements", desc: "Broadcast to sections", icon: Bell },
            { to: "/app/teacher/payroll", title: "Faculty Payslips", desc: "Salary structures & pay stubs", icon: GraduationCap },
            { to: "/app/teacher/hub", title: "Open Campus Directory", desc: "Campus offices & faculty directory", icon: Compass }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                className="rounded-xl border border-line bg-panel p-4 shadow-2xs hover:border-brand-500 hover:bg-surface/50 transition flex items-start gap-3 group"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-500/10 text-brand-600">
                  <Icon size={18} />
                </div>
                <div>
                  <p className="text-sm font-bold text-ink group-hover:text-brand-600 transition">{item.title}</p>
                  <p className="text-xs text-muted mt-0.5">{item.desc}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
