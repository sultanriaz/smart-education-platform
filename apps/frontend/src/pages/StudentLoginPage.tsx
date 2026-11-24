import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  Eye,
  EyeOff,
  ArrowLeft,
  Sparkles,
  ShieldCheck
} from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../features/auth/useAuth";
import { hasAnyRole } from "../features/auth/permissions";
import { runtimeConfig } from "../lib/runtime-config";

const DEPARTMENTS = [
  { code: "BCS", label: "BS Computer Science (BCS)" },
  { code: "BSE", label: "BS Software Engineering (BSE)" },
  { code: "BEE", label: "BS Electrical Engineering (BEE)" },
  { code: "BBA", label: "BS Business Administration (BBA)" },
  { code: "BME", label: "BS Mechanical Engineering (BME)" },
  { code: "MCS", label: "Master of Computer Science (MCS)" }
];

export function StudentLoginPage() {
  const { state, user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [department, setDepartment] = useState("BCS");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (state === "authenticated" && user && hasAnyRole(user.roles, ["student"])) {
    const requested =
      location.state &&
      typeof location.state === "object" &&
      "from" in location.state &&
      typeof (location.state as { from?: unknown }).from === "string" &&
      (location.state as { from: string }).from.startsWith("/app/student")
        ? (location.state as { from: string }).from
        : "/app/student";
    return <Navigate to={requested} replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setServerError("");

    const cleanReg = registrationNumber.trim();
    if (!cleanReg) {
      setServerError("Please enter your Registration Number (e.g., 155).");
      return;
    }
    if (!password) {
      setServerError("Please enter your password.");
      return;
    }

    const identifier = cleanReg.includes("@") || cleanReg.includes("-")
      ? cleanReg
      : `${department}-${cleanReg}`;

    try {
      setSubmitting(true);
      await login({ email: identifier, password }, "student");
      const requested =
        location.state &&
        typeof location.state === "object" &&
        "from" in location.state &&
        typeof (location.state as { from?: unknown }).from === "string" &&
        (location.state as { from: string }).from.startsWith("/app/student")
          ? (location.state as { from: string }).from
          : "/app/student";
      navigate(requested, { replace: true });
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : "Student sign in failed. Check your credentials."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemoStudent = () => {
    setDepartment("BCS");
    setRegistrationNumber("155");
    setPassword("StudentPass123!");
    setServerError("");
  };

  return (
    <main className="auth-layout relative">
      <aside className="auth-story">
        <div className="flex items-center gap-3">
          <span className="brand-mark">
            <GraduationCap size={23} />
          </span>
          <strong className="text-xl tracking-tight">Student Portal</strong>
        </div>
        <div>
          <div className="text-xs font-semibold tracking-widest text-hero-accent">
            STUDENT ACADEMIC ACCESS
          </div>
          <h2>
            Your Courses, Attendance &amp; Progress.<br />
            <span>All in One Cockpit.</span>
          </h2>
          <p>
            Select your department and enter your registration number to inspect enrolled subjects, attendance bars, assignments, quizzes, marks, and lecture resources.
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
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-ink hover:underline transition"
            >
              <ArrowLeft size={14} />
              <span>Main Dashboard</span>
            </Link>
          </div>

          <h1 className="mt-2 text-2xl font-bold">Student Portal Login</h1>
          <p className="mt-1 text-sm leading-6 text-muted">
            Sign in with your Department, Registration Number, and Password.
          </p>

          {/* Demo Student Quick-Fill */}
          <div className="mt-4 rounded-2xl border border-line bg-surface/70 p-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-primary-ink">
              <Sparkles size={14} />
              <span>Demo Student: BCS-155</span>
            </div>
            <button
              type="button"
              onClick={fillDemoStudent}
              className="rounded-lg border border-line bg-panel px-2.5 py-1 text-xs font-semibold text-ink hover:border-primary hover:text-primary-ink transition"
            >
              Auto-Fill BCS-155
            </button>
          </div>

          <form className="mt-5 space-y-4" onSubmit={(e) => void handleSubmit(e)} noValidate>
            <div>
              <label htmlFor="student-dept" className="block text-sm font-medium text-ink mb-1.5">
                Department
              </label>
              <select
                id="student-dept"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full rounded-xl border border-line bg-panel px-3.5 py-2.5 text-sm text-ink focus:outline-hidden focus:ring-2 focus:ring-primary"
              >
                {DEPARTMENTS.map((d) => (
                  <option key={d.code} value={d.code}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Registration Number"
              type="text"
              autoComplete="username"
              placeholder="e.g., 155"
              value={registrationNumber}
              onChange={(e) => setRegistrationNumber(e.target.value)}
            />

            {registrationNumber.trim() && (
              <p className="text-xs text-muted -mt-2">
                Signing in as:{" "}
                <strong className="font-mono text-primary-ink">
                  {registrationNumber.trim().includes("-") || registrationNumber.trim().includes("@")
                    ? registrationNumber.trim()
                    : `${department}-${registrationNumber.trim()}`}
                </strong>
              </p>
            )}

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
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
                className="rounded-xl border border-danger/40 bg-danger-soft p-3 text-xs font-semibold text-danger-ink"
              >
                {serverError}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Verifying Student Credentials…" : "Sign In to Student Portal"}
            </Button>
          </form>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-line pt-4 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <ShieldCheck size={14} className="text-success-ink" />
              <span>Student-only access enforced</span>
            </span>
            <Link to="/login/faculty" className="font-semibold text-secondary-ink hover:underline">
              Are you a Teacher? Faculty Login →
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
