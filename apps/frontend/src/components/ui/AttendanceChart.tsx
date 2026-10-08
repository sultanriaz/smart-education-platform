import { useMemo } from "react";
import type { AttendanceRecord } from "../../features/student/types";

export function AttendanceChart({ records }: { records: AttendanceRecord[] }) {
  const points = useMemo(() => {
    const buckets = new Map<string, { attended: number; total: number }>();
    records.forEach(row => {
      if (!row.sessionDate || row.status.toUpperCase() === "EXCUSED") return;
      const day = row.sessionDate.slice(0, 10);
      const item = buckets.get(day) ?? { attended: 0, total: 0 };
      item.total++;
      if (["PRESENT", "LATE"].includes(row.status.toUpperCase())) item.attended++;
      buckets.set(day, item);
    });
    return [...buckets].sort(([a], [b]) => a.localeCompare(b)).slice(-7).map(([day, item]) => ({ day, percent: Math.round(item.attended / item.total * 100) }));
  }, [records]);
  if (!points.length) return <div className="chart-empty">Your attendance pattern will appear after your first recorded session.</div>;
  return <div className="attendance-chart" role="img" aria-label={points.map(p => `${p.day}: ${p.percent}% attended`).join(", ")}><div className="chart-bars">{points.map(point => <div className="chart-column" key={point.day}><span>{point.percent}%</span><div className="chart-track"><div style={{ height: `${point.percent}%` }} /></div><time dateTime={point.day}>{new Date(`${point.day}T12:00:00`).toLocaleDateString([], { day: "numeric", month: "short" })}</time></div>)}</div><p>Last {points.length} recorded days · present and late count as attended</p></div>;
}
