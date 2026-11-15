import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { Check, X as XIcon, Eye, EyeOff, Moon, Sun, GraduationCap } from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import {
  register as registerAccount,
  requestEmailVerification
} from "../features/auth/auth-api";

const strongPassword = z
  .string()
  .min(12, "Use at least 12 characters.")
  .max(128, "Use at most 128 characters.")
  .regex(/[a-z]/, "Add a lowercase letter.")
  .regex(/[A-Z]/, "Add an uppercase letter.")
  .regex(/[0-9]/, "Add a number.")
  .regex(/[^A-Za-z0-9]/, "Add a symbol.");

const schema = z
  .object({
    full_name: z.string().min(2, "Enter your full name.").max(120),
    email: z.string().email("Enter a valid email address."),
    password: strongPassword,
    confirmPassword: z.string()
  })
  .refine((values) => values.password === values.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords do not match."
  });

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema), mode: "onChange" });

  const watchedPassword = watch("password") || "";

  const criteria = [
    { label: "At least 12 characters", met: watchedPassword.length >= 12 },
    { label: "One uppercase letter (A-Z)", met: /[A-Z]/.test(watchedPassword) },
    { label: "One lowercase letter (a-z)", met: /[a-z]/.test(watchedPassword) },
    { label: "One number (0-9)", met: /[0-9]/.test(watchedPassword) },
    { label: "One special symbol (!@#$...)", met: /[^A-Za-z0-9]/.test(watchedPassword) },
  ];

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

  const onSubmit = handleSubmit(async (input) => {
    const values = { full_name: input.full_name, email: input.email, password: input.password };
    setServerError("");
    try {
      await registerAccount(values);

      try {
        await requestEmailVerification(values.email);
      } catch {
        // Do not turn an already-successful registration into a visible failure.
      }

      navigate(
        `/verify-email/request?email=${encodeURIComponent(values.email)}`,
        { replace: true }
      );
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : "Registration failed."
      );
    }
  });

  return (
    <main className="subtle-grid relative flex min-h-screen items-center justify-center px-4 py-10">
      {/* Quick Theme Toggle */}
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

      <section className="panel w-full max-w-md p-7 sm:p-8 shadow-md">
        <div className="flex items-center gap-2 mb-4 text-brand-700">
          <GraduationCap size={28} />
          <span className="font-bold text-xl tracking-tight text-ink">EduSphere</span>
        </div>

        <h1 className="text-2xl font-bold">Create student account</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Public registration creates a Student account. Teacher and Admin accounts
          are provisioned by university administrators.
        </p>

        <form className="mt-7 space-y-4" onSubmit={onSubmit} noValidate>
          <Input
            label="Full name"
            autoComplete="name"
            error={errors.full_name?.message}
            {...register("full_name")}
          />
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
              autoComplete="new-password"
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

          {/* Interactive Criteria Checklist */}
          {watchedPassword.length > 0 && (
            <div className="rounded-xl border border-line bg-surface/50 p-3 space-y-1.5 text-xs">
              <span className="font-semibold text-muted block mb-1">Password Requirements:</span>
              {criteria.map((c, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-2 transition ${
                    c.met ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-muted"
                  }`}
                >
                  {c.met ? (
                    <Check size={14} className="text-emerald-600 dark:text-emerald-400 shrink-0" />
                  ) : (
                    <XIcon size={14} className="text-muted/60 shrink-0" />
                  )}
                  <span>{c.label}</span>
                </div>
              ))}
            </div>
          )}

          <div className="relative">
            <Input
              label="Confirm password"
              type={showConfirm ? "text" : "password"}
              autoComplete="new-password"
              error={errors.confirmPassword?.message}
              {...register("confirmPassword")}
            />
            <button
              type="button"
              aria-label={showConfirm ? "Hide confirm password" : "Show confirm password"}
              onClick={() => setShowConfirm(!showConfirm)}
              className="absolute right-3 top-[38px] text-muted hover:text-text transition"
            >
              {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
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
            {isSubmitting ? "Creating account…" : "Register"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{" "}
          <Link className="font-semibold text-brand-700 hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
