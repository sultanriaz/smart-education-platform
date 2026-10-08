export function FullPageLoader({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surface p-6" role="status">
      <div className="panel flex items-center gap-3 px-5 py-4">
        <span
          className="h-5 w-5 animate-spin rounded-full border-2 border-brand-100 border-t-brand-600"
          aria-hidden="true"
        />
        <span className="text-sm font-medium text-ink">{label}</span>
      </div>
    </div>
  );
}
