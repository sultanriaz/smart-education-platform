import { Link } from "react-router-dom";
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

function sameDay(value: string, now = new Date()) {
  const date = new Date(value);
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

export function TeacherDashboardPage() {
  const sections = useTeacherSections();
  const timetable = useTeacherTimetable();
  const assignments = useTeacherAssignments();
  const unread = useUnreadCount();

  if (
    sections.isLoading &&
    timetable.isLoading &&
    assignments.isLoading &&
    unread.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading teacher dashboard…" />
      </div>
    );
  }

  const error =
    sections.error ?? timetable.error ?? assignments.error ?? unread.error;
  const today = (timetable.data ?? []).filter((item) => sameDay(item.startsAt));
  const activeAssignments = (assignments.data ?? []).filter(
    (item) => new Date(item.dueAt).getTime() >= Date.now()
  );

  return (
    <div className="page-container">
      <DashboardWelcome subtitle="A clearer day for you. A better learning experience for your students. Bring your teaching together." action="Take class attendance" to="/app/teacher/attendance" />

      {error ? (
        <div className="mb-5">
          <InlineError message="Some teacher dashboard data could not be loaded. Individual modules may still be available." />
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Assigned sections"
          value={sections.data?.length ?? "—"}
          helper="Academic sections currently assigned to you."
        />
        <StatCard
          label="Classes today"
          value={timetable.data ? today.length : "—"}
          helper="Your scheduled teaching sessions."
        />
        <StatCard
          label="Active assessments"
          value={assignments.data ? activeAssignments.length : "—"}
          helper="Assignments whose deadlines have not passed."
        />
        <StatCard
          label="Unread notifications"
          value={unread.data ?? "—"}
          helper="Messages and platform updates."
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="Today's teaching">
          {today.length ? (
            <div className="space-y-3">
              {today.map((item) => (
                <div key={item.id} className="rounded-xl border border-line p-4">
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
                    {" · "}
                    {item.roomId ?? "Room TBA"}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">{timetable.error ? "Teaching schedule is unavailable." : "No teaching sessions are scheduled today."}</p>
          )}
          <Link
            to="/app/teacher/timetable"
            className="mt-4 inline-flex text-sm font-semibold text-brand-700 hover:underline"
          >
            Open timetable
          </Link>
        </Card>

        <Card title="Quick actions">
          <div className="grid gap-3 sm:grid-cols-2">
            {([
              ["/app/teacher/attendance", "Take attendance"],
              ["/app/teacher/learning", "Publish resources"],
              ["/app/teacher/assessments", "Manage assessments"],
              ["/app/teacher/announcements", "Send announcement"],
              ["/app/teacher/facilities", "Book facility"],
              ["/app/notifications", "Open inbox"]
            ] as const).map(([path, label]) => (
              <Link
                key={path}
                to={path}
                className="rounded-xl border border-line bg-panel px-4 py-3 text-sm font-semibold hover:bg-surface"
              >
                {label}
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
