import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { GraduationCap, Eye, EyeOff, Moon, Sun, Sparkles } from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";
import { runtimeConfig } from "../lib/runtime-config";

const schema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password.")
});
type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { state, user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

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
      setServerError(error instanceof Error ? error.message : "Sign in failed.");
    }
  });

  const fillDemoAccount = (role: "admin" | "teacher" | "student") => {
    if (role === "admin") {
      setValue("email", "admin@smartedu.local", { shouldValidate: true });
      setValue("password", "AdminPass123!", { shouldValidate: true });
    } else if (role === "teacher") {
      setValue("email", "teacher@demo.example.edu", { shouldValidate: true });
      setValue("password", "Q7!Oa8xZ24L2aX0dEnj8TuSWGEoDgN-vY8KxEVrnts6cbAaZ", { shouldValidate: true });
    } else {
      setValue("email", "student@demo.example.edu", { shouldValidate: true });
      setValue("password", "Q7!vEpzlshyGXIddiaOLN7GT73b1cUc71pLVJ1ybXGm5dUaZ", { shouldValidate: true });
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
          <strong className="text-xl tracking-tight">EduSphere</strong>
        </div>
        <div>
          <div className="text-xs tracking-widest text-violet-300">YOUR CONNECTED CAMPUS</div>
          <h2>
            One workspace.<br />
            <span>Endless possibilities.</span>
          </h2>
          <p>
            Learn with purpose. Teach with confidence. Bring every part of your academic day together.
          </p>
        </div>
        <footer>COMSATS University Islamabad · Sahiwal Campus</footer>
      </aside>

      <div className="auth-form-area">
        <section>
          <p className="auth-overline">{runtimeConfig.appName}</p>
          <h1 className="mt-2 text-2xl font-bold">Welcome back</h1>
          <p className="mt-2 text-sm leading-6 text-muted">
            Sign in to your Student, Teacher, or Admin workspace.
          </p>

          {/* 1-Click Demo Accounts Quick-Select */}
          <div className="mt-5 rounded-2xl border border-line bg-surface/60 p-3">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-700">
              <Sparkles size={14} />
              <span>Quick-Fill Demo Credentials:</span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => fillDemoAccount("student")}
                className="rounded-lg border border-line bg-panel px-2.5 py-1 text-xs font-semibold text-text hover:border-brand-500 hover:text-brand-600 transition"
              >
                🎓 Student
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount("teacher")}
                className="rounded-lg border border-line bg-panel px-2.5 py-1 text-xs font-semibold text-text hover:border-brand-500 hover:text-brand-600 transition"
              >
                📚 Teacher
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount("admin")}
                className="rounded-lg border border-line bg-panel px-2.5 py-1 text-xs font-semibold text-text hover:border-brand-500 hover:text-brand-600 transition"
              >
                🛡️ Admin
              </button>
            </div>
          </div>

          <form className="mt-6 space-y-4" onSubmit={onSubmit} noValidate>
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              error={errors.email?.message}
              {...register("email")}
            />

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
                className="text-sm font-semibold text-brand-700 hover:underline"
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
              {isSubmitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <div className="mt-6 space-y-2 text-center text-sm text-muted">
            <p>
              Need a Student account?{" "}
              <Link className="font-semibold text-brand-700 hover:underline" to="/register">
                Register
              </Link>
            </p>
            <p>
              Missing a verification email?{" "}
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
