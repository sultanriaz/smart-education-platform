import { Card } from "./Card";
import { Activity, ArrowUpRight } from "lucide-react";

export function StatCard({
  label,
  value,
  helper
}: {
  label: string;
  value: string | number;
  helper?: string;
}) {
  return (
    <Card>
      <div className="stat-label text-xs font-semibold text-muted">{label}<span className="stat-icon"><Activity size={16} /></span></div>
      <p className="stat-value mt-3 text-3xl font-bold tracking-tight text-ink">{value}</p>
      {helper ? <p className="mt-3 text-xs leading-5 text-muted">{helper}</p> : null}
      <ArrowUpRight size={12} className="absolute right-5 bottom-5 text-muted opacity-40" aria-hidden="true" />
    </Card>
  );
}
