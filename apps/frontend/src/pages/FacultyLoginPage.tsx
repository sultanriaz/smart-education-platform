import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Eye,
  EyeOff,
  Moon,
  Sun,
  ArrowLeft,
  Sparkles,
  Lock
} from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../features/auth/useAuth";
import { hasAnyRole } from "../features/auth/permissions";
import { runtimeConfig } from "../lib/runtime-config";

export function FacultyLoginPage() {
  const { state, user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("sep-theme", next);
    } catch {
      // ignore
    }
  };

  if (state === "authenticated" && user && hasAnyRole(user.roles, ["teacher"])) {
    const requested =
      location.state &&
      typeof location.state === "object" &&
      "from" in location.state &&
      typeof (location.state as { from?: unknown }).from === "string" &&
      (location.state as { from: string }).from.startsWith("/app/teacher")
        ? (location.state as { from: string }).from
        : "/app/teacher";
    return <Navigate to={requested} replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setServerError("");

    const cleanId = identifier.trim();
    if (!cleanId) {
      setServerError("Enter your Faculty Employee ID or institutional email.");
      return;
    }
    if (!password) {
      setServerError("Enter your password.");
      return;
    }

    try {
      setSubmitting(true);
      await login({ email: cleanId, password }, "teacher");
      const requested =
        location.state &&
        typeof location.state === "object" &&
        "from" in location.state &&
        typeof (location.state as { from?: unknown }).from === "string" &&
        (location.state as { from: string }).from.startsWith("/app/teacher")
          ? (location.state as { from: string }).from
          : "/app/teacher";
      navigate(requested, { replace: true });
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : "Faculty sign in failed. Check your teacher credentials."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemoFaculty = () => {
    setIdentifier("FAC-101");
    setPassword("TeacherPass123!");
    setServerError("");
  };

  return (
    <main className="auth-layout relative">
      <div className="absolute right-5 top-5 z-20">
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-line bg-panel text-muted hover:text-ink transition shadow-xs"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>

      <aside className="auth-story">
        <div className="flex items-center gap-3">
          <span className="brand-mark">
            <BookOpen size={23} />
          </span>
          <strong className="text-xl tracking-tight">Faculty Portal</strong>
        </div>
        <div>
          <div className="text-xs font-semibold tracking-widest text-indigo-300">
            TEACHER-ONLY RESTRICTED ACCESS
          </div>
          <h2>
            Teaching Schedules, Grading &amp; Attendance.<br />
            <span>Built for Faculty.</span>
          </h2>
          <p>
            Restricted strictly to authorized faculty members. Manage weekly lecture rosters, mark class attendance, publish assessments, and reserve lecture rooms.
          </p>
        </div>
        <footer>COMSATS University Islamabad · Sahiwal Campus</footer>
      </aside>

      <div className="auth-form-area">
        <section>
          <div className="flex items-center justify-between">
            <p className="auth-overline">{runtimeConfig.appName}</p>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition"
            >
              <ArrowLeft size={14} />
              <span>Main Dashboard</span>
            </Link>
          </div>

          <h1 className="mt-2 text-2xl font-bold">Faculty Login</h1>
          <p className="mt-1 text-sm leading-6 text-muted">
            Teachers only. Sign in with your verified Faculty ID or institutional email.
          </p>

          {/* Demo Faculty Quick-Fill */}
          <div className="mt-4 rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-300">
              <Sparkles size={14} />
              <span>Demo Teacher: Sir Munir (FAC-101)</span>
            </div>
            <button
              type="button"
              onClick={fillDemoFaculty}
              className="rounded-lg border border-line bg-panel px-2.5 py-1 text-xs font-semibold text-ink hover:border-indigo-500 hover:text-indigo-600 transition"
            >
              Auto-Fill FAC-101
            </button>
          </div>

          <form className="mt-5 space-y-4" onSubmit={(e) => void handleSubmit(e)} noValidate>
            <Input
              label="Faculty Employee ID or Email"
              type="text"
              autoComplete="username"
              placeholder="e.g., FAC-101 or teacher@smartedu.local"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your faculty password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute right-3 top-9 text-muted hover:text-ink transition"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {serverError && (
              <div
                role="alert"
                className="rounded-xl border border-danger/30 bg-danger/10 p-3 text-xs font-semibold text-danger"
              >
                {serverError}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Verifying Faculty Credentials…" : "Sign In to Faculty Portal"}
            </Button>
          </form>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-line pt-4 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <Lock size={13} className="text-indigo-600" />
              <span>Teacher credentials strictly enforced</span>
            </span>
            <Link to="/login/student" className="font-semibold text-brand-600 hover:underline">
              Student? Go to Student Portal →
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
