export function InlineError({ message }: { message: string }) {
  return (
    <div
      className="rounded-xl border border-danger/40 bg-danger-soft px-4 py-3 text-sm text-danger-ink"
      role="alert"
    >
      {message}
    </div>
  );
}
