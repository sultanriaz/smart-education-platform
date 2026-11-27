export function SectionLoader({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="panel min-h-40 space-y-4 p-6"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <span
          className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-brand-100 border-t-brand-600"
          aria-hidden="true"
        />
        <span className="text-sm font-medium text-muted">{label}</span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 animate-pulse" aria-hidden="true">
        <div className="h-16 rounded-xl bg-subtle/75" />
        <div className="h-16 rounded-xl bg-subtle/75" />
        <div className="h-16 rounded-xl bg-subtle/75" />
      </div>
    </div>
  );
}
