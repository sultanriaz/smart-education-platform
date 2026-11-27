import { Link } from "react-router-dom";
import { Compass, ArrowLeft, Home } from "lucide-react";

export function NotFoundPage() {
  return (
    <main className="subtle-grid flex min-h-dvh items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center shadow-lg">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink">
          <Compass size={32} aria-hidden="true" />
        </div>
        <p className="mt-4 text-xs font-bold tracking-widest text-primary-ink uppercase">HTTP 404</p>
        <h1 className="mt-2 text-2xl font-bold">Page Not Found</h1>
        <p className="mt-3 text-sm leading-6 text-muted">
          The requested route or resource does not exist, has been archived, or moved to a new address.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/app"
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>Return to Dashboard</span>
          </Link>
          <Link
            to="/"
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line bg-panel px-5 py-2.5 text-sm font-semibold text-ink hover:bg-surface transition"
          >
            <Home size={16} aria-hidden="true" />
            <span>Campus Explorer</span>
          </Link>
        </div>
      </section>
    </main>
  );
}
