import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { GraduationCap } from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";
import { runtimeConfig } from "../lib/runtime-config";

const schema = z.object({
  email: z.string().email("Enter a valid email address."),
  // Do not enforce the new password policy at sign-in. Existing accounts may
  // predate Sprint 18 and server-side authentication remains authoritative.
  password: z.string().min(1, "Enter your password.")
});
type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { state, user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

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

  return (
    <main className="auth-layout">
      <aside className="auth-story"><div className="flex items-center gap-3"><span className="brand-mark"><GraduationCap size={23} /></span><strong className="text-xl tracking-tight">EduSphere</strong></div><div><div className="text-xs tracking-widest text-violet-300">YOUR CONNECTED CAMPUS</div><h2>One workspace.<br /><span>Endless possibilities.</span></h2><p>Learn with purpose. Teach with confidence. Bring every part of your academic day together.</p></div><footer>COMSATS University Islamabad · Sahiwal Campus</footer></aside>
      <div className="auth-form-area"><section>
        <p className="auth-overline">{runtimeConfig.appName}</p>
        <h1 className="mt-2 text-2xl font-bold">Welcome back</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Sign in to your Student, Teacher, or Admin workspace.
        </p>

        <form className="mt-7 space-y-4" onSubmit={onSubmit} noValidate>
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            error={errors.email?.message}
            {...register("email")}
          />
          <Input
            label="Password"
            type="password"
            autoComplete="current-password"
            error={errors.password?.message}
            {...register("password")}
          />
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
              className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-danger"
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
      </section></div>
    </main>
  );
}
