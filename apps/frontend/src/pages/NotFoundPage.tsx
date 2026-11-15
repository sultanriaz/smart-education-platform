import { Link } from "react-router-dom";
import { Compass, ArrowLeft } from "lucide-react";

export function NotFoundPage() {
  return (
    <main className="subtle-grid flex min-h-screen items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center shadow-lg">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-950/50">
          <Compass size={32} />
        </div>
        <p className="mt-4 text-xs font-bold tracking-widest text-brand-700 uppercase">HTTP 404</p>
        <h1 className="mt-2 text-2xl font-bold">Page Not Found</h1>
        <p className="mt-3 text-sm leading-6 text-muted">
          The requested route or resource does not exist, has been archived, or moved to a new address.
        </p>
        <Link
          to="/app"
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 transition"
        >
          <ArrowLeft size={16} />
          <span>Return to Dashboard</span>
        </Link>
      </section>
    </main>
  );
}
