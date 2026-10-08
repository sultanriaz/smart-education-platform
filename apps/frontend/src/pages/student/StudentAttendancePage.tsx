import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { ProgressBar } from "../../components/ui/ProgressBar";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import {
  useAttendanceRecords,
  useAttendanceSummary
} from "../../features/student/hooks";

export function StudentAttendancePage() {
  const summary = useAttendanceSummary();
  const records = useAttendanceRecords();

  if (summary.isLoading || records.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading attendance…" />
      </div>
    );
  }

  if (summary.error || records.error) {
    return (
      <div className="page-container">
        <PageHeader title="My attendance" eyebrow="Student" />
        <InlineError message="Attendance data could not be loaded." />
      </div>
    );
  }

  const s = summary.data!;

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student"
        title="My attendance"
        description="Review your overall attendance and session-by-session history."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Attendance" value={`${s.percentage.toFixed(1)}%`} />
        <StatCard label="Present" value={s.present} />
        <StatCard label="Late" value={s.late} />
        <StatCard label="Absent" value={s.absent} />
        <StatCard label="Excused" value={s.excused} />
      </div>

      <Card className="mt-6" title="Overall attendance">
        <ProgressBar value={s.percentage} label="Attendance percentage" />
        <p className="mt-3 text-xs text-muted">
          Total considered sessions: {s.totalConsidered}. Excused sessions are
          displayed separately and are expected to follow the Attendance
          Service's configured percentage policy.
        </p>
      </Card>

      <Card className="mt-6" title="Attendance history">
        {records.data?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                  <th className="px-3 py-3">Date</th>
                  <th className="px-3 py-3">Course</th>
                  <th className="px-3 py-3">Status</th>
                  <th className="px-3 py-3">Notes</th>
                </tr>
              </thead>
              <tbody>
                {records.data.map((record) => (
                  <tr key={record.id} className="border-b border-line/70">
                    <td className="px-3 py-3">
                      {record.sessionDate
                        ? new Date(record.sessionDate).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="px-3 py-3">
                      {record.courseLabel ?? record.courseId ?? record.sectionId ?? "—"}
                    </td>
                    <td className="px-3 py-3">
                      <Badge>{record.status}</Badge>
                    </td>
                    <td className="px-3 py-3 text-muted">
                      {record.notes ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-muted">No attendance records are available yet.</p>
        )}
      </Card>
    </div>
  );
}
