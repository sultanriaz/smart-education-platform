import { Link } from "react-router-dom";

export function ForbiddenPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center">
        <p className="text-sm font-semibold text-danger">403</p>
        <h1 className="mt-2 text-2xl font-bold">Access not permitted</h1>
        <p className="mt-3 text-sm leading-6 text-muted">Your current role does not have access to this area.</p>
        <Link to="/app" className="mt-6 inline-flex rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white">
          Return to dashboard
        </Link>
      </section>
    </main>
  );
}
