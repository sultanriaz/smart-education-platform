import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center">
        <p className="text-sm font-semibold text-brand-700">404</p>
        <h1 className="mt-2 text-2xl font-bold">Page not found</h1>
        <p className="mt-3 text-sm text-muted">The requested page does not exist or has moved.</p>
        <Link to="/app" className="mt-6 inline-flex rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white">
          Open dashboard
        </Link>
      </section>
    </main>
  );
}
