import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { useToast } from "../../components/ui/useToast";
import * as api from "../../features/admin/admin-api";
import {
  adminKeys,
  useAdminMutation,
  useReportSnapshots,
  useReportingOverview
} from "../../features/admin/hooks";

type MetricName =
  | "attendance"
  | "assessments"
  | "facilities"
  | "notifications"
  | "scheduling"
  | "enrollment";

const metricNames: MetricName[] = [
  "attendance",
  "assessments",
  "facilities",
  "notifications",
  "scheduling",
  "enrollment"
];

export function AdminReportingPage() {
  const overview = useReportingOverview();
  const snapshots = useReportSnapshots();
  const toast = useToast();
  const [metric, setMetric] = useState<MetricName>("attendance");

  const metricRows = useQuery({
    queryKey: ["admin", "reporting", "metric", metric],
    queryFn: () => api.getMetricRows(metric)
  });

  const createSnapshot = useAdminMutation(
    ({ reportType }: { reportType: string }) =>
      api.createReportSnapshot(reportType, {}),
    adminKeys.snapshots
  );

  if (overview.isLoading || snapshots.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading reporting dashboard…" />
      </div>
    );
  }

  if (overview.error || snapshots.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Reporting & analytics" />
        <InlineError message="Reporting data could not be loaded." />
      </div>
    );
  }

  const value = overview.data!;

  const download = async () => {
    try {
      await api.downloadReportCsv(metric);
      toast.push(`${metric} CSV downloaded.`, "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Export failed.", "error");
    }
  };

  const snapshot = async () => {
    try {
      await createSnapshot.mutateAsync({ reportType: metric });
      toast.push("Report snapshot created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Snapshot failed.", "error");
    }
  };

  const columns = metricRows.data?.length
    ? Array.from(
        new Set(metricRows.data.flatMap((row) => Object.keys(row)))
      ).slice(0, 12)
    : [];

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Reporting & analytics"
        description="Read aggregated operational metrics from Reporting Service without cross-service database joins."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Active enrollments" value={value.activeEnrollments} />
        <StatCard
          label="Attendance"
          value={
            value.attendancePercentage != null
              ? `${value.attendancePercentage.toFixed(1)}%`
              : "—"
          }
          helper={`${value.attendanceRecords} attendance records`}
        />
        <StatCard
          label="Assessment average"
          value={
            value.assessmentAveragePercent != null
              ? `${value.assessmentAveragePercent.toFixed(1)}%`
              : "—"
          }
          helper={`${value.gradedAttempts} graded attempts`}
        />
        <StatCard
          label="Assessment pass rate"
          value={
            value.assessmentPassRate != null
              ? `${value.assessmentPassRate.toFixed(1)}%`
              : "—"
          }
        />
        <StatCard
          label="Facility bookings"
          value={value.facilityBookings}
          helper={`${value.approvedFacilityBookings} approved`}
        />
        <StatCard
          label="Notification deliveries"
          value={value.notificationDeliveries}
          helper={
            value.notificationSuccessRate != null
              ? `${value.notificationSuccessRate.toFixed(1)}% success`
              : "Success rate unavailable"
          }
        />
        <StatCard label="Schedule changes" value={value.scheduleChanges} />
      </div>

      <Card className="mt-6" title="Metric explorer">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="block flex-1 text-sm font-medium">
            Metric
            <select
              className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
              value={metric}
              onChange={(event) => setMetric(event.target.value as MetricName)}
            >
              {metricNames.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <Button variant="secondary" onClick={() => void snapshot()}>
            Create snapshot
          </Button>
          <Button onClick={() => void download()}>Download CSV</Button>
        </div>

        <div className="mt-5">
          {metricRows.isLoading ? (
            <SectionLoader label="Loading metric rows…" />
          ) : metricRows.error ? (
            <InlineError message="Metric rows could not be loaded." />
          ) : metricRows.data?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-left text-sm">
                <thead>
                  <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                    {columns.map((column) => (
                      <th key={column} className="px-2 py-3">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {metricRows.data.slice(0, 200).map((row, index) => (
                    <tr key={index} className="border-b border-line/70">
                      {columns.map((column) => (
                        <td key={column} className="px-2 py-3">
                          {typeof row[column] === "object"
                            ? JSON.stringify(row[column])
                            : String(row[column] ?? "—")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-muted">No rows exist for this metric.</p>
          )}
        </div>
      </Card>

      <Card className="mt-6" title="Saved report snapshots">
        <div className="space-y-3">
          {(snapshots.data ?? []).map((item) => (
            <details key={item.id} className="rounded-xl border border-line p-3">
              <summary className="cursor-pointer text-sm font-semibold">
                {item.reportType} · {new Date(item.createdAt).toLocaleString()}
              </summary>
              <pre className="mt-3 max-h-72 overflow-auto rounded-xl bg-surface p-3 text-xs">
                {JSON.stringify(item.payload, null, 2)}
              </pre>
            </details>
          ))}
          {!(snapshots.data ?? []).length ? (
            <p className="text-sm text-muted">No snapshots have been created yet.</p>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
