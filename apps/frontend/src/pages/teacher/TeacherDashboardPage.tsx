import { useState } from "react";
import { Link } from "react-router-dom";
import {
  GraduationCap,
  Clock,
  MapPin,
  CheckCircle2,
  Calendar,
  ClipboardCheck,
  ArrowUpRight,
  Sparkles,
  BookOpen,
  Users,
  Bell,
  Compass,
  Building,
  Check,
  AlertCircle
} from "lucide-react";

import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { useUnreadCount } from "../../features/student/hooks";
import {
  useTeacherAssignments,
  useTeacherSections,
  useTeacherTimetable
} from "../../features/teacher/hooks";

interface TodayLecture {
  id: string;
  courseCode: string;
  courseTitle: string;
  section: string;
  slot: string;
  time: string;
  room: string;
  enrolledStudents: number;
  attendanceMarked: boolean;
}

const DEFAULT_TODAY_LECTURES: TodayLecture[] = [
  {
    id: "lec-1",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    section: "BCS-7C",
    slot: "Slot 2",
    time: "10:15 AM – 11:45 AM",
    room: "Room C-204 (C Block, 2nd Floor)",
    enrolledStudents: 54,
    attendanceMarked: false
  },
  {
    id: "lec-2",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction Lab",
    section: "BCS-7A",
    slot: "Slot 4",
    time: "02:00 PM – 03:30 PM",
    room: "Software Lab 2 (C Block, Ground Floor)",
    enrolledStudents: 48,
    attendanceMarked: false
  },
  {
    id: "lec-3",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence",
    section: "BCS-8B",
    slot: "Slot 5",
    time: "03:45 PM – 05:15 PM",
    room: "Room A-201 (A Block, 2nd Floor)",
    enrolledStudents: 50,
    attendanceMarked: true
  }
];

export function TeacherDashboardPage() {
  const sections = useTeacherSections();
  const timetable = useTeacherTimetable();
  const assignments = useTeacherAssignments();
  const unread = useUnreadCount();

  const [lectures, setLectures] = useState<TodayLecture[]>(DEFAULT_TODAY_LECTURES);

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

  const activeAssignments = (assignments.data ?? []).filter(
    (item) => new Date(item.dueAt).getTime() >= Date.now()
  );

  const toggleAttendanceQuick = (id: string) => {
    setLectures((prev) =>
      prev.map((l) => (l.id === id ? { ...l, attendanceMarked: !l.attendanceMarked } : l))
    );
  };

  return (
    <div className="page-container space-y-6">
      <DashboardWelcome
        subtitle="Dr. Munir Ahmad · Faculty of Computer Science. Manage your lecture timetable, class attendance, and evaluations."
        action="Take Class Attendance"
        to="/app/teacher/attendance"
      />

      {error ? (
        <div className="mb-2">
          <InlineError message="Some live schedule feeds could not be synchronized. Local teaching schedule remains active." />
        </div>
      ) : null}

      {/* Top Academic Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Today's Lectures"
          value={`${lectures.length} Lectures`}
          helper="Next: Compiler Construction (BCS-7C) at 10:15 AM."
        />
        <StatCard
          label="Assigned Sections"
          value={sections.data?.length ? `${sections.data.length} Sections` : "3 Sections"}
          helper="BCS-7C, BCS-7A, BCS-8B."
        />
        <StatCard
          label="Pending Grading"
          value="4 Submissions"
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
              Click "Mark Attendance" to submit attendance for that section or launch the full roster.
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
          {lectures.map((lec) => (
            <div
              key={lec.id}
              className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/60 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="flex items-start gap-4">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl font-bold font-mono text-xs shadow-xs ${
                    lec.attendanceMarked
                      ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/30"
                      : "bg-brand-500/10 text-brand-600 border border-brand-500/30"
                  }`}
                >
                  {lec.slot}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-brand-600">{lec.courseCode}</span>
                    <span className="rounded-md bg-surface px-2 py-0.5 text-xs font-semibold text-text">
                      Section: {lec.section}
                    </span>
                    <span className="text-xs text-muted font-medium">({lec.enrolledStudents} Students)</span>
                    {lec.attendanceMarked ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600">
                        <Check size={12} /> Attendance Taken
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600">
                        <Clock size={12} /> Pending Submission
                      </span>
                    )}
                  </div>

                  <h3 className="font-bold text-base text-ink mt-1">{lec.courseTitle}</h3>

                  <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted">
                    <span className="flex items-center gap-1">
                      <Clock size={13} className="text-brand-600" />
                      <span>{lec.time}</span>
                    </span>
                    <span>·</span>
                    <span className="flex items-center gap-1">
                      <MapPin size={13} className="text-brand-600" />
                      <span>{lec.room}</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-stretch md:self-auto justify-end">
                <button
                  type="button"
                  onClick={() => toggleAttendanceQuick(lec.id)}
                  className={`rounded-xl px-3.5 py-2 text-xs font-semibold transition shadow-2xs ${
                    lec.attendanceMarked
                      ? "border border-line bg-surface text-muted hover:text-ink"
                      : "bg-emerald-600 text-white hover:bg-emerald-700"
                  }`}
                >
                  {lec.attendanceMarked ? "Mark as Pending" : "1-Click Attendance"}
                </button>

                <Link
                  to="/app/teacher/attendance"
                  className="inline-flex items-center gap-1 rounded-xl bg-brand-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-brand-700 transition shadow-xs"
                >
                  <span>Open Roster</span>
                  <ArrowUpRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ================= 2. PENDING SUBMISSIONS & ROOM RESERVATION ================= */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pending Grading Card */}
        <Card title="Pending Assessment Submissions" description="Student submissions awaiting evaluation and marks entry.">
          <div className="space-y-3 mt-2">
            <div className="rounded-xl border border-line bg-surface/50 p-4 flex items-center justify-between">
              <div>
                <p className="font-bold text-sm text-ink">Compiler Construction: Assignment 1 (Flex)</p>
                <p className="text-xs text-muted mt-0.5">Section BCS-7C · 52 of 54 submitted</p>
              </div>
              <span className="rounded-md bg-amber-500/10 px-2.5 py-1 text-xs font-bold text-amber-600">
                4 to Grade
              </span>
            </div>

            <div className="rounded-xl border border-line bg-surface/50 p-4 flex items-center justify-between">
              <div>
                <p className="font-bold text-sm text-ink">Artificial Intelligence: Midterm Lab Project</p>
                <p className="text-xs text-muted mt-0.5">Section BCS-8B · 48 of 50 submitted</p>
              </div>
              <span className="rounded-md bg-emerald-500/10 px-2.5 py-1 text-xs font-bold text-emerald-600">
                All Graded
              </span>
            </div>

            <Link
              to="/app/teacher/assessments"
              className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-brand-600 hover:underline"
            >
              <span>Manage all course assessments</span>
              <ArrowUpRight size={13} />
            </Link>
          </div>
        </Card>

        {/* Free Slot & Room Reservation Card */}
        <Card title="Make-up Class & Room Reservation" description="Locate and reserve unoccupied classrooms across campus blocks.">
          <div className="space-y-3 mt-2">
            <p className="text-xs text-muted leading-relaxed">
              Need to schedule a makeup lecture or project viva? Browse current room availability or reserve a lab:
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <Link
                to="/explore"
                className="rounded-xl border border-line bg-surface/60 p-3 hover:border-brand-500 transition group"
              >
                <p className="font-bold text-ink group-hover:text-brand-600 transition">A Block Rooms</p>
                <p className="text-[11px] text-muted">A-102 & A-202 Free</p>
              </Link>
              <Link
                to="/explore"
                className="rounded-xl border border-line bg-surface/60 p-3 hover:border-brand-500 transition group"
              >
                <p className="font-bold text-ink group-hover:text-brand-600 transition">C Block Rooms</p>
                <p className="text-[11px] text-muted">C-102 & C-201 Free</p>
              </Link>
            </div>

            <div className="pt-2 flex items-center justify-between">
              <Link
                to="/app/teacher/facilities"
                className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-brand-700 transition"
              >
                <Building size={14} />
                <span>Reserve Facility or Lab</span>
              </Link>

              <Link
                to="/explore"
                className="text-xs font-semibold text-brand-600 hover:underline"
              >
                View Live Free Slots
              </Link>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Action Matrix */}
      <Card title="Faculty Modules & Services" description="Direct access to teaching tools and administrative services.">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 mt-3">
          {[
            { to: "/app/teacher/attendance", title: "Class Attendance", desc: "Digital attendance roster", icon: CheckCircle2 },
            { to: "/app/teacher/learning", title: "Lecture Resources", desc: "Upload slides & notes", icon: BookOpen },
            { to: "/app/teacher/assessments", title: "Quizzes & Grading", desc: "Create tests and evaluate", icon: ClipboardCheck },
            { to: "/app/teacher/announcements", title: "Announcements", desc: "Broadcast to sections", icon: Bell },
            { to: "/app/teacher/payroll", title: "Faculty Payslips", desc: "Salary structures & pay stubs", icon: GraduationCap },
            { to: "/explore", title: "Open Campus Directory", desc: "Campus bus & office directory", icon: Compass }
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
