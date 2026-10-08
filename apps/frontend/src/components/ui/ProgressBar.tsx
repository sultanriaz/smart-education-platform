export function ProgressBar({
  value,
  label
}: {
  value: number;
  label: string;
}) {
  const bounded = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-xs">
        <span className="font-medium text-ink">{label}</span>
        <span className="text-muted">{bounded.toFixed(1)}%</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-surface"
        role="progressbar"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={bounded}
      >
        <div
          className="h-full rounded-full bg-brand-600"
          style={{ width: `${bounded}%` }}
        />
      </div>
    </div>
  );
}
