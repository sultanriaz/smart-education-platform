export function FullPageLoader({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="min-h-dvh bg-surface p-6 sm:p-8"
      role="status"
      aria-live="polite"
    >
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="panel p-6 space-y-4">
          <div className="flex items-center gap-3">
            <span
              className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-brand-100 border-t-brand-600"
              aria-hidden="true"
            />
            <span className="text-sm font-medium text-ink">{label}</span>
          </div>
          <div className="space-y-2.5 animate-pulse" aria-hidden="true">
            <div className="h-5 w-48 rounded-lg bg-subtle" />
            <div className="h-3.5 w-72 max-w-full rounded-md bg-subtle/80" />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 animate-pulse" aria-hidden="true">
          <div className="panel h-32 p-5" />
          <div className="panel h-32 p-5" />
        </div>
      </div>
    </div>
  );
}
