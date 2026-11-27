import { RotateCcw } from "lucide-react";

export function InlineError({
  message,
  onRetry,
  retryLabel = "Retry",
  isRetrying = false,
}: {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  isRetrying?: boolean;
}) {
  return (
    <div
      className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-danger/40 bg-danger-soft px-4 py-3 text-sm text-danger-ink"
      role="alert"
    >
      <span className="min-w-0 flex-1 leading-6">{message}</span>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          disabled={isRetrying}
          className="inline-flex min-h-11 shrink-0 items-center gap-1.5 rounded-xl border border-danger/40 bg-panel px-3.5 py-2 text-xs font-semibold text-danger-ink transition hover:bg-danger/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RotateCcw className={`h-3.5 w-3.5 ${isRetrying ? "animate-spin" : ""}`} aria-hidden="true" />
          <span>{isRetrying ? "Retrying…" : retryLabel}</span>
        </button>
      ) : null}
    </div>
  );
}
