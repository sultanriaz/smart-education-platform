export function InlineError({ message }: { message: string }) {
  return (
    <div
      className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger"
      role="alert"
    >
      {message}
    </div>
  );
}
