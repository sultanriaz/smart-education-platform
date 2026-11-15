import { AttendanceChart } from "../../components/ui/AttendanceChart";
import { Link } from "react-router-dom";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { Sparkles, BookOpen, CreditCard, Calendar, ClipboardCheck, ArrowUpRight } from "lucide-react";
import {
  useAssessmentAssignments,
  useAttendanceSummary,
  useAttendanceRecords,
  useTimetable,
  useUnreadCount
} from "../../features/student/hooks";

function isToday(value: string) {
  if (!value) return false;
  const date = new Date(value);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

export function StudentDashboardPage() {
  const attendance = useAttendanceSummary();
  const records = useAttendanceRecords();
  const timetable = useTimetable();
  const assignments = useAssessmentAssignments();
  const unread = useUnreadCount();

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
        <SectionLoader label="Loading student dashboard…" />
      </div>
    );
  }

  const today = (timetable.data ?? []).filter((item) => isToday(item.startsAt));
  const upcoming = (assignments.data ?? [])
    .filter((item) => {
      const due = new Date(item.dueAt).getTime();
      return Number.isFinite(due) && due >= Date.now();
    })
    .sort((a, b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime())
    .slice(0, 4);

  return (
    <div className="page-container">
      <DashboardWelcome subtitle="Your next class, your next milestone, your next possibility. Here's your day at a glance." action="Explore your timetable" to="/app/student/timetable" />

      {criticalError ? (
        <div className="mb-5">
          <InlineError message="Some dashboard data could not be loaded. You can still open individual modules." />
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Attendance"
          value={
            attendance.data
              ? `${attendance.data.percentage.toFixed(1)}%`
              : "—"
          }
          helper="Present and late sessions count as attended."
        />
        <StatCard
          label="Classes today"
          value={timetable.data ? today.length : "—"}
          helper="From your current timetable."
        />
        <StatCard
          label="Upcoming assessments"
          value={assignments.data ? upcoming.length : "—"}
          helper="Nearest due assessments."
        />
        <StatCard
          label="Unread notifications"
          value={unread.data ?? "—"}
          helper="Open your inbox for details."
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2" title="Your attendance, over time" description="Small steps make a strong semester.">
          {records.error ? <InlineError message="Attendance history could not be loaded." /> : records.isLoading ? <SectionLoader label="Loading attendance history…" /> : <AttendanceChart records={records.data ?? []} />}
        </Card>
        <Card title="Quick Navigation" description="Explore your student modules.">
          <div className="grid gap-2.5 mt-4">
            <Link
              to="/app/student/learning"
              className="flex items-center justify-between rounded-xl border border-line p-3 hover:border-brand-500 hover:bg-surface transition group"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950/50">
                  <Sparkles size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-text group-hover:text-brand-600 transition">
                    AI Self-Learning Hub
                  </p>
                  <p className="text-xs text-muted">Adaptive practice & notes</p>
                </div>
              </div>
              <ArrowUpRight size={16} className="text-muted group-hover:text-brand-600 transition" />
            </Link>

            <Link
              to="/app/student/finance"
              className="flex items-center justify-between rounded-xl border border-line p-3 hover:border-brand-500 hover:bg-surface transition group"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50">
                  <CreditCard size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-text group-hover:text-emerald-600 transition">
                    Fee & Payments
                  </p>
                  <p className="text-xs text-muted">Invoices & installments</p>
                </div>
              </div>
              <ArrowUpRight size={16} className="text-muted group-hover:text-emerald-600 transition" />
            </Link>

            <Link
              to="/app/student/assessments"
              className="flex items-center justify-between rounded-xl border border-line p-3 hover:border-brand-500 hover:bg-surface transition group"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950/50">
                  <ClipboardCheck size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-text group-hover:text-blue-600 transition">
                    Academic Quizzes
                  </p>
                  <p className="text-xs text-muted">Course exams & scores</p>
                </div>
              </div>
              <ArrowUpRight size={16} className="text-muted group-hover:text-blue-600 transition" />
            </Link>

            <Link
              to="/app/student/facilities"
              className="flex items-center justify-between rounded-xl border border-line p-3 hover:border-brand-500 hover:bg-surface transition group"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-50 text-purple-600 dark:bg-purple-950/50">
                  <Calendar size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-text group-hover:text-purple-600 transition">
                    Campus Facilities
                  </p>
                  <p className="text-xs text-muted">Book study rooms & labs</p>
                </div>
              </div>
              <ArrowUpRight size={16} className="text-muted group-hover:text-purple-600 transition" />
            </Link>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card
          title="Today's timetable"
          description="Your scheduled classes for today."
        >
          {today.length ? (
            <ul className="space-y-3">
              {today.map((item) => (
                <li
                  key={item.id}
                  className="rounded-xl border border-line bg-surface/50 p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="font-semibold">{item.title}</p>
                      <p className="mt-1 text-xs text-muted">
                        {new Date(item.startsAt).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit"
                        })}
                        {" – "}
                        {new Date(item.endsAt).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit"
                        })}
                      </p>
                    </div>
                    <span className="text-xs text-muted">
                      {item.roomLabel ?? "Room TBA"}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted">{timetable.error ? "Today’s classes are unavailable." : "No classes scheduled for today."}</p>
          )}

          <Link
            to="/app/student/timetable"
            className="mt-4 inline-flex text-sm font-semibold text-brand-700 hover:underline"
          >
            Open full timetable
          </Link>
        </Card>

        <Card
          title="Upcoming assessments"
          description="Assessments with the nearest deadlines."
        >
          {upcoming.length ? (
            <ul className="space-y-3">
              {upcoming.map((item) => (
                <li
                  key={item.id}
                  className="rounded-xl border border-line bg-surface/50 p-3"
                >
                  <p className="font-semibold">{item.title}</p>
                  <p className="mt-1 text-xs text-muted">
                    Due {new Date(item.dueAt).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted">{assignments.error ? "Assessments are unavailable." : "No upcoming assessments."}</p>
          )}

          <Link
            to="/app/student/assessments"
            className="mt-4 inline-flex text-sm font-semibold text-brand-700 hover:underline"
          >
            Open assessments
          </Link>
        </Card>
      </div>
    </div>
  );
}
