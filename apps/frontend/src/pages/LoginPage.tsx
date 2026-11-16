import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import {
  GraduationCap,
  Eye,
  EyeOff,
  Moon,
  Sun,
  Sparkles,
  Compass,
  ArrowRight,
  UserCheck,
  Building2,
  BookOpen
} from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";
import { runtimeConfig } from "../lib/runtime-config";

const schema = z.object({
  email: z.string().min(1, "Enter your Student Reg No, Employee ID, or institutional email."),
  password: z.string().min(1, "Enter your password.")
});
type FormValues = z.infer<typeof schema>;

const DEPARTMENTS = [
  { code: "BCS", label: "BS Computer Science (BCS)" },
  { code: "BSE", label: "BS Software Engineering (BSE)" },
  { code: "BEE", label: "BS Electrical Engineering (BEE)" },
  { code: "BBA", label: "BS Business Administration (BBA)" },
  { code: "BME", label: "BS Mechanical Engineering (BME)" },
  { code: "MCS", label: "Master of Computer Science (MCS)" }
];

export function LoginPage() {
  const { state, user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");
  const [mode, setMode] = useState<"universal" | "student_reg">("universal");
  const [selectedDept, setSelectedDept] = useState("BCS");
  const [regNumber, setRegNumber] = useState("");

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  });

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

  if (state === "authenticated" && user) {
    const role = primaryRole(user.roles);
    return <Navigate to={role ? `/app/${role}` : "/app"} replace />;
  }

  const handleStudentRegChange = (dept: string, num: string) => {
    setSelectedDept(dept);
    setRegNumber(num);
    const cleanNum = num.trim();
    if (cleanNum) {
      setValue("email", `${dept}-${cleanNum}`, { shouldValidate: true });
    } else {
      setValue("email", "", { shouldValidate: false });
    }
  };

  const onSubmit = handleSubmit(async (values) => {
    setServerError("");
    try {
      await login(values);
      const requested =
        location.state &&
        typeof location.state === "object" &&
        "from" in location.state &&
        typeof (location.state as { from?: unknown }).from === "string"
          ? (location.state as { from: string }).from
          : "/app";
      navigate(requested, { replace: true });
    } catch (error) {
      setServerError(error instanceof Error ? error.message : "Sign in failed. Check your credentials.");
    }
  });

  const fillDemoAccount = (role: "admin" | "teacher" | "student") => {
    setMode("universal");
    if (role === "admin") {
      setValue("email", "admin@smartedu.local", { shouldValidate: true });
      setValue("password", "AdminPass123!", { shouldValidate: true });
    } else if (role === "teacher") {
      setValue("email", "FAC-101", { shouldValidate: true });
      setValue("password", "TeacherPass123!", { shouldValidate: true });
    } else {
      setValue("email", "BCS-155", { shouldValidate: true });
      setValue("password", "StudentPass123!", { shouldValidate: true });
    }
  };

  return (
    <main className="auth-layout relative">
      {/* Quick Theme Toggle in Top Right */}
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
            <GraduationCap size={23} />
          </span>
          <strong className="text-xl tracking-tight">SmartEdu Platform</strong>
        </div>
        <div>
          <div className="text-xs font-semibold tracking-widest text-violet-300">UNIVERSAL CAMPUS GATEWAY</div>
          <h2>
            Unified Academic Access.<br />
            <span>Students, Faculty & Community.</span>
          </h2>
          <p>
            Log in once with your Student Registration Number, Employee ID, or Institutional Email to access your personalized role-adaptive workspace.
          </p>
        </div>
        <footer>COMSATS University Islamabad · Sahiwal Campus</footer>
      </aside>

      <div className="auth-form-area">
        <section>
          <div className="flex items-center justify-between">
            <p className="auth-overline">{runtimeConfig.appName}</p>
            <Link
              to="/explore"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition"
            >
              <Compass size={14} />
              <span>Campus Explorer</span>
            </Link>
          </div>

          <h1 className="mt-2 text-2xl font-bold">Universal Gateway</h1>
          <p className="mt-1 text-sm leading-6 text-muted">
            Sign in to your Student, Teacher, or Administrative workspace.
          </p>

          {/* 1-Click Demo Accounts Quick-Select */}
          <div className="mt-4 rounded-2xl border border-line bg-surface/70 p-3 shadow-2xs">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-700 dark:text-brand-400">
              <Sparkles size={14} />
              <span>Quick-Fill Live Personas:</span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => fillDemoAccount("student")}
                className="flex items-center justify-center gap-1.5 rounded-lg border border-line bg-panel px-2.5 py-1.5 text-xs font-medium text-text hover:border-brand-500 hover:text-brand-600 transition shadow-2xs"
              >
                🎓 <span>Student (155)</span>
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount("teacher")}
                className="flex items-center justify-center gap-1.5 rounded-lg border border-line bg-panel px-2.5 py-1.5 text-xs font-medium text-text hover:border-brand-500 hover:text-brand-600 transition shadow-2xs"
              >
                📚 <span>Faculty (Munir)</span>
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount("admin")}
                className="flex items-center justify-center gap-1.5 rounded-lg border border-line bg-panel px-2.5 py-1.5 text-xs font-medium text-text hover:border-brand-500 hover:text-brand-600 transition shadow-2xs"
              >
                🛡️ <span>Admin</span>
              </button>
            </div>
          </div>

          {/* Mode Tabs: Universal ID vs Student Reg Helper */}
          <div className="mt-5 flex rounded-xl border border-line bg-surface p-1 text-xs">
            <button
              type="button"
              onClick={() => setMode("universal")}
              className={`flex-1 rounded-lg py-1.5 font-medium transition ${
                mode === "universal"
                  ? "bg-panel text-brand-700 dark:text-brand-300 font-semibold shadow-xs"
                  : "text-muted hover:text-text"
              }`}
            >
              Universal ID / Email
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("student_reg");
                handleStudentRegChange(selectedDept, regNumber);
              }}
              className={`flex-1 rounded-lg py-1.5 font-medium transition ${
                mode === "student_reg"
                  ? "bg-panel text-brand-700 dark:text-brand-300 font-semibold shadow-xs"
                  : "text-muted hover:text-text"
              }`}
            >
              Student Reg No Helper
            </button>
          </div>

          <form className="mt-5 space-y-4" onSubmit={onSubmit} noValidate>
            {mode === "universal" ? (
              <div>
                <Input
                  label="Identifier (Reg No, Employee ID, or Email)"
                  type="text"
                  autoComplete="username"
                  placeholder="e.g. BCS-155, FAC-101, or name@smartedu.local"
                  error={errors.email?.message}
                  {...register("email")}
                />
              </div>
            ) : (
              <div className="space-y-3 rounded-xl border border-line/70 bg-surface/40 p-3">
                <div>
                  <label className="block text-xs font-semibold text-text mb-1">Department</label>
                  <select
                    value={selectedDept}
                    onChange={(e) => handleStudentRegChange(e.target.value, regNumber)}
                    className="w-full rounded-xl border border-line bg-panel px-3 py-2 text-sm text-text focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                  >
                    {DEPARTMENTS.map((d) => (
                      <option key={d.code} value={d.code}>
                        {d.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-text mb-1">Registration Number</label>
                  <input
                    type="text"
                    placeholder="e.g. 155"
                    value={regNumber}
                    onChange={(e) => handleStudentRegChange(selectedDept, e.target.value)}
                    className="w-full rounded-xl border border-line bg-panel px-3 py-2 text-sm text-text focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                  />
                  <p className="mt-1 text-xs text-muted">
                    Resolved identifier: <span className="font-mono font-semibold text-brand-600">{watch("email") || "—"}</span>
                  </p>
                </div>
              </div>
            )}

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                error={errors.password?.message}
                {...register("password")}
              />
              <button
                type="button"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[38px] text-muted hover:text-text transition"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <div className="text-right">
              <Link
                className="text-xs font-semibold text-brand-700 hover:underline"
                to="/forgot-password"
              >
                Forgot password?
              </Link>
            </div>

            {serverError ? (
              <div
                className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-danger dark:border-red-900/60 dark:bg-red-950/40"
                role="alert"
              >
                {serverError}
              </div>
            ) : null}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Authenticating…" : "Sign In to Workspace"}
            </Button>
          </form>

          {/* Open Campus Explorer Callout */}
          <div className="mt-6 rounded-2xl border border-line bg-surface/50 p-3.5 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-bold text-text flex items-center gap-1.5">
                <Compass size={14} className="text-brand-600" />
                Visiting or Prospective Student?
              </p>
              <p className="text-xs text-muted mt-0.5">
                Browse shuttle schedules, directory, sports gala & free study rooms without credentials.
              </p>
            </div>
            <Link
              to="/explore"
              className="shrink-0 inline-flex items-center gap-1 rounded-lg bg-panel px-3 py-1.5 text-xs font-semibold text-brand-600 border border-line hover:border-brand-500 transition shadow-2xs"
            >
              <span>Explore</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="mt-5 space-y-2 text-center text-xs text-muted">
            <p>
              Need a Student account?{" "}
              <Link className="font-semibold text-brand-700 hover:underline" to="/register">
                Register with Email
              </Link>
            </p>
            <p>
              Missing verification email?{" "}
              <Link
                className="font-semibold text-brand-700 hover:underline"
                to="/verify-email/request"
              >
                Request another
              </Link>
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
