export function SectionLoader({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="panel flex min-h-32 items-center justify-center gap-3 p-6" role="status">
      <span
        className="h-5 w-5 animate-spin rounded-full border-2 border-brand-100 border-t-brand-600"
        aria-hidden="true"
      />
      <span className="text-sm text-muted">{label}</span>
    </div>
  );
}
