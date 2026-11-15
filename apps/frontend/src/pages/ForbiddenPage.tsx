import { Link } from "react-router-dom";
import { ShieldAlert, ArrowLeft, LogOut } from "lucide-react";
import { useAuth } from "../features/auth/useAuth";

export function ForbiddenPage() {
  const { logout } = useAuth();

  return (
    <main className="subtle-grid flex min-h-screen items-center justify-center p-6">
      <section className="panel max-w-lg p-8 text-center shadow-lg">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-red-100 text-danger dark:bg-red-950/50">
          <ShieldAlert size={32} />
        </div>

        <p className="mt-4 text-xs font-bold tracking-widest text-danger uppercase">HTTP 403 Forbidden</p>
        <h1 className="mt-2 text-2xl font-bold">Access Not Permitted</h1>
        <p className="mt-3 text-sm leading-6 text-muted">
          Your active account does not have authorization to view this area. If you believe this is in error, contact your university administrator.
        </p>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/app"
            className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 transition"
          >
            <ArrowLeft size={16} />
            <span>Return to workspace</span>
          </Link>
          <button
            type="button"
            onClick={() => void logout()}
            className="inline-flex items-center gap-2 rounded-xl border border-line bg-panel px-4 py-2.5 text-sm font-semibold text-muted hover:text-text transition"
          >
            <LogOut size={16} />
            <span>Switch account</span>
          </button>
        </div>
      </section>
    </main>
  );
}
