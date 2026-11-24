import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  Sparkles,
  BookOpen,
  CreditCard,
  Calendar,
  ClipboardCheck,
  ArrowUpRight,
  AlertTriangle,
  Clock,
  MapPin,
  CheckCircle2,
  FileText,
  Bell,
  Video,
  Info,
  ChevronRight,
  Compass,
  Bus,
  Search,
  ArrowRight,
  Activity,
  ShieldAlert
} from "lucide-react";

import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { AttendanceChart } from "../../components/ui/AttendanceChart";
import {
  useAssessmentAssignments,
  useAttendanceSummary,
  useAttendanceRecords,
  useTimetable,
  useUnreadCount
} from "../../features/student/hooks";
import { COURSES_CATALOG, type EnrolledCourse } from "../../features/student/courses-data";

export function StudentDashboardPage() {
  const navigate = useNavigate();
  const attendance = useAttendanceSummary();
  const records = useAttendanceRecords();
  const timetable = useTimetable();
  const assignments = useAssessmentAssignments();
  const unread = useUnreadCount();

  // Timer countdown computation for next upcoming class
  const [countdownMinutes, setCountdownMinutes] = useState(28);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdownMinutes((prev) => (prev > 1 ? prev - 1 : 45));
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const criticalError =
    attendance.error ?? timetable.error ?? assignments.error ?? unread.error;

  if (
    attendance.isLoading &&
    timetable.isLoading &&
    assignments.isLoading &&
    unread.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading student cockpit…" />
      </div>
    );
  }

  // Find course with regulatory attendance risk (<75%)
  const riskCourse = COURSES_CATALOG.find((c) => c.attendance.percentage < 75);

  return (
    <div className="page-container space-y-6">
      <DashboardWelcome
        subtitle="Academic Cockpit & Course Command Centers. Track attendance compliance, upcoming deadlines, and grades."
        action="Open Timetable"
        to="/app/student/timetable"
      />

      {criticalError ? (
        <div className="mb-2">
          <InlineError message="Some live schedule data could not be synchronized. Your course command centers remain active." />
        </div>
      ) : null}

      {/* ================= 1. REGULATORY ATTENDANCE ALERT BAR ================= */}
      {riskCourse && (
        <div className="rounded-2xl border border-danger/40 bg-danger-soft p-4 sm:p-5 text-danger-ink shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-danger text-danger-fg shadow-xs">
              <ShieldAlert size={22} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <strong className="text-sm font-bold">Attendance Regulatory Compliance Alert</strong>
                <span className="rounded-full bg-danger px-2 py-0.2 text-[10px] font-bold uppercase text-danger-fg">
                  Exam Risk
                </span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-danger-ink">
                Your attendance in <strong>{riskCourse.title} ({riskCourse.code})</strong> is currently{" "}
                <span className="font-bold underline">{riskCourse.attendance.percentage}%</span>, falling below the mandatory{" "}
                <strong>75% HEC / University regulatory examination cutoff</strong>. You must attend the next{" "}
                <strong>{riskCourse.attendance.requiredConsecutive} consecutive lectures</strong> to be cleared to sit in the terminal examination.
              </p>
            </div>
          </div>
          <Link
            to={`/app/student/courses/${riskCourse.id}`}
            className="shrink-0 rounded-xl bg-danger px-4 py-2 text-xs font-bold text-danger-fg shadow-xs hover:opacity-90 transition"
          >
            Open Attendance Ledger &amp; Excuses
          </Link>
        </div>
      )}

      {/* ================= 2. UPCOMING CLASS COUNTDOWN BANNER ================= */}
      <div className="rounded-2xl border border-primary/30 bg-gradient-to-r from-primary-soft/80 via-primary-soft/30 to-transparent p-5 shadow-2xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary text-on-primary shadow-xs">
            <Clock size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-primary-ink">
                Next Upcoming Class
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-success-soft px-2 py-0.5 text-[11px] font-semibold text-success-ink">
                <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                Starts in {countdownMinutes} mins
              </span>
            </div>
            <h2 className="text-lg font-bold text-ink mt-0.5">
              Compiler Construction <span className="text-xs font-normal text-muted">(CSC-354 · Section BCS-7C)</span>
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted">
              <span className="flex items-center gap-1">
                <MapPin size={13} className="text-primary-ink" />
                <strong>Room C-204</strong> (C Block, 2nd Floor)
              </span>
              <span>·</span>
              <span>
                Instructor: <strong>Dr. Munir Ahmad</strong>
              </span>
              <span>·</span>
              <span className="font-mono">Slot 2 (10:15 AM – 11:45 AM)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 self-stretch md:self-auto justify-end">
          <Link
            to="/app/student/courses/compiler"
            className="rounded-xl border border-line bg-panel px-3.5 py-2 text-xs font-bold text-primary-ink hover:border-primary transition shadow-2xs"
          >
            Course Command Center
          </Link>
          <Link
            to="/app/student/timetable"
            className="inline-flex items-center gap-1 rounded-xl bg-primary px-3.5 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition shadow-xs"
          >
            <span>Full Schedule</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* Top Academic Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Cumulative Attendance"
          value={attendance.data ? `${attendance.data.percentage.toFixed(1)}%` : "82.2%"}
          helper="Weighted across all enrolled subjects."
        />
        <StatCard
          label="Enrolled Courses"
          value={`${COURSES_CATALOG.length} Subjects`}
          helper="14 Total Credit Hours this semester."
        />
        <StatCard
          label="Pending Assignments"
          value="2 Pending"
          helper="Nearest: Compiler Construction tomorrow."
        />
        <StatCard
          label="Unread Notifications"
          value={unread.data ?? "3"}
          helper="Instructor announcements & notices."
        />
      </div>

      {/* ================= 3. HIGH-DENSITY COURSE COCKPIT CARDS ================= */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-ink">Enrolled Subject Command Centers</h2>
            <p className="text-xs text-muted">
              High-density interactive cards. Click any course to launch its 4-tab consolidated workspace.
            </p>
          </div>
          <span className="text-xs font-semibold text-primary-ink hidden sm:inline">
            Active Semester: Fall 2026 / Spring 2026
          </span>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4">
          {COURSES_CATALOG.map((course) => {
            const attPct = course.attendance.percentage;
            const isGreen = attPct >= 80;
            const isAmber = attPct >= 75 && attPct < 80;
            const isRed = attPct < 75;

            return (
              <div
                key={course.id}
                onClick={() => navigate(`/app/student/courses/${course.id}`)}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-primary hover:shadow-md transition flex flex-col justify-between group space-y-4"
              >
                {/* Course Header & Section Badge */}
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-black text-primary-ink bg-primary-soft px-2 py-0.5 rounded-md">
                      {course.code}
                    </span>
                    <span className="rounded-md bg-surface px-2 py-0.5 text-[11px] font-bold text-muted border border-line">
                      {course.section} · {course.creditHours} Cr
                    </span>
                  </div>

                  <h3 className="mt-2.5 text-base font-bold text-ink group-hover:text-primary-ink transition leading-snug">
                    {course.title}
                  </h3>

                  {/* Instructor with Avatar & Online Status */}
                  <div className="mt-2.5 flex items-center gap-2 pt-2 border-t border-line/60">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface font-bold text-xs text-primary-ink border border-line">
                      {course.teacher.avatar}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-ink truncate">{course.teacher.name}</p>
                      <p className="text-[10px] text-muted truncate">
                        <span className={course.teacher.status.includes("Office") ? "text-success-ink" : "text-warning-ink"}>●</span> {course.teacher.status}
                      </p>
                    </div>
                  </div>

                  {/* Attendance Dial / Progress Bar */}
                  <div className="mt-4 space-y-1.5 rounded-xl border border-line/60 bg-surface/50 p-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-muted">Attendance</span>
                      <span
                        className={`font-mono font-bold ${
                          isGreen ? "text-success-ink" : isAmber ? "text-warning-ink" : "text-danger-ink"
                        }`}
                      >
                        {course.attendance.percentage}% ({course.attendance.attended}/{course.attendance.total})
                      </span>
                    </div>

                    <div className="h-2 w-full overflow-hidden rounded-full bg-surface">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isGreen ? "bg-success" : isAmber ? "bg-warning" : "bg-danger"
                        }`}
                        style={{ width: `${Math.min(course.attendance.percentage, 100)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-muted pt-0.5">
                      <span>Status:</span>
                      <span
                        className={`font-semibold ${
                          isGreen ? "text-success-ink" : isAmber ? "text-warning-ink" : "text-danger-ink font-bold"
                        }`}
                      >
                        {isGreen ? "Compliant (≥80%)" : isAmber ? "Borderline (75-79%)" : "At Risk (<75%)"}
                      </span>
                    </div>
                  </div>

                  {/* Current Standing & Next Deadline */}
                  <div className="mt-3 space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Current Standing:</span>
                      <span className="font-mono font-bold text-ink">{course.standing.estimatedGrade}</span>
                    </div>
                    <div className="text-[11px] text-muted line-clamp-1 pt-0.5">
                      <strong className="text-ink">Next:</strong> {course.standing.nextDeadline}
                    </div>
                  </div>
                </div>

                {/* Bottom Action Footer */}
                <div className="pt-3 border-t border-line/60 flex items-center justify-between text-xs font-bold text-primary-ink">
                  <span>Course Command Center</span>
                  <ArrowRight size={14} className="group-hover:translate-x-1 transition" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ================= 4. QUICK ACTION DOCK ================= */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          to="/app/student/facilities"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-primary transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent-ink">
            <Clock size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-primary-ink transition">Free Slots Finder</p>
            <p className="text-xs text-muted">A, C, D Block study rooms</p>
          </div>
        </Link>

        <Link
          to="/app/student/transit"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-secondary transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-secondary-soft text-secondary-ink">
            <Bus size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-secondary-ink transition">Shuttle Tracker</p>
            <p className="text-xs text-muted">Farid Town &amp; City bus timings</p>
          </div>
        </Link>

        <Link
          to="/app/student/learning"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-primary transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary-ink">
            <Sparkles size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-primary-ink transition">AI Self-Assessment</p>
            <p className="text-xs text-muted">Smart practice &amp; KaTeX solutions</p>
          </div>
        </Link>

        <Link
          to="/app/student/hub"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-accent transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent-ink">
            <Compass size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-accent-ink transition">Campus Directory</p>
            <p className="text-xs text-muted">Faculty offices &amp; department labs</p>
          </div>
        </Link>
      </div>

      {/* Attendance History Graph */}
      <Card title="Attendance Progression Over Semester" description="Official academic session presence tracking.">
        {records.error ? (
          <InlineError message="Attendance history could not be loaded." />
        ) : records.isLoading ? (
          <SectionLoader label="Loading attendance history…" />
        ) : (
          <AttendanceChart records={records.data ?? []} />
        )}
      </Card>
    </div>
  );
}
