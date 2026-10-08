import { AttendanceChart } from "../../components/ui/AttendanceChart";
import { Link } from "react-router-dom";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
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
        <Card title="Make room for progress" description="Everything you need for your next step.">
          <div className="grid gap-3 mt-5">{([["/app/student/learning", "Browse learning resources"], ["/app/student/assessments", "Check your assessments"], ["/app/student/facilities", "Book a study space"]] as const).map(([to, label]) => <Link key={to} to={to} className="rounded-xl border border-line p-4 text-sm font-medium hover:bg-surface transition">{label} <span aria-hidden="true" className="float-right text-brand-700">↗</span></Link>)}</div>
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
