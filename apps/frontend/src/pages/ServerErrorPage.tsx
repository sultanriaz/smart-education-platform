import { Link } from "react-router-dom";
import { ServerCrash, RotateCcw, Home, ArrowLeft } from "lucide-react";

export function ServerErrorPage({ onRetry }: { onRetry?: () => void }) {
  return (
    <main className="subtle-grid flex min-h-dvh items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center shadow-lg">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-danger-soft text-danger-ink">
          <ServerCrash size={32} aria-hidden="true" />
        </div>
        <p className="mt-4 text-xs font-bold tracking-widest text-danger-ink uppercase">HTTP 500</p>
        <h1 className="mt-2 text-2xl font-bold">Server or Application Error</h1>
        <p className="mt-3 text-sm leading-6 text-muted">
          An unexpected error interrupted this request. You can reload the page or return safely to the portal home.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <button
            type="button"
            onClick={() => (onRetry ? onRetry() : window.location.reload())}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
          >
            <RotateCcw size={16} aria-hidden="true" />
            <span>Try Again</span>
          </button>
          <Link
            to="/app"
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line bg-panel px-4 py-2.5 text-sm font-semibold text-ink hover:bg-surface transition"
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>Dashboard</span>
          </Link>
          <Link
            to="/"
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line bg-panel px-4 py-2.5 text-sm font-semibold text-muted hover:text-ink transition"
          >
            <Home size={16} aria-hidden="true" />
            <span>Campus Explorer</span>
          </Link>
        </div>
      </section>
    </main>
  );
}
