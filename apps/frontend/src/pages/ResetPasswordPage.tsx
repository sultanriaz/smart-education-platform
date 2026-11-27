import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation } from "react-router-dom";
import { z } from "zod";
import { Eye, EyeOff } from "lucide-react";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { resetPassword } from "../features/auth/auth-api";

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
    password: strongPassword,
    confirmPassword: z.string()
  })
  .refine((values) => values.password === values.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords do not match."
  });

type FormValues = z.infer<typeof schema>;

export function ResetPasswordPage() {
  const location = useLocation();
  const token = useMemo(() => {
    const params = new URLSearchParams(location.hash.replace(/^#/, ""));
    return params.get("token") ?? "";
  }, [location.hash]);
  useEffect(() => {
    if (!location.hash) return;
    window.history.replaceState(
      null,
      "",
      `${location.pathname}${location.search}`
    );
  }, [location.hash, location.pathname, location.search]);

  const [complete, setComplete] = useState(false);
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = handleSubmit(async ({ password }) => {
    setServerError("");
    if (!token) {
      setServerError("The password-reset link is incomplete.");
      return;
    }
    try {
      await resetPassword(token, password);
      setComplete(true);
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : "Password reset failed."
      );
    }
  });

  return (
    <main className="subtle-grid flex min-h-dvh items-center justify-center px-4 py-10">
      <section className="panel w-full max-w-md p-7 sm:p-8">
        <h1 className="text-2xl font-bold">Choose a new password</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Use 12–128 characters with uppercase, lowercase, a number, and a symbol.
        </p>

        {complete ? (
          <div className="mt-6 space-y-4">
            <div className="rounded-xl border border-line bg-surface p-4 text-sm">
              Your password was changed and previous refresh sessions were revoked.
            </div>
            <Link
              className="inline-flex min-h-11 items-center font-semibold text-brand-700 hover:underline"
              to="/login"
            >
              Sign in with the new password
            </Link>
          </div>
        ) : (
          <form className="mt-7 space-y-4" onSubmit={onSubmit} noValidate>
            <div className="relative">
              <Input
                label="New password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                className="pr-12"
                error={errors.password?.message}
                {...register("password")}
              />
              <button
                type="button"
                aria-label={showPassword ? "Hide new password" : "Show new password"}
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute right-1 top-[30px] inline-flex h-11 w-11 items-center justify-center rounded-lg text-muted hover:text-ink transition"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <div className="relative">
              <Input
                label="Confirm password"
                type={showConfirm ? "text" : "password"}
                autoComplete="new-password"
                className="pr-12"
                error={errors.confirmPassword?.message}
                {...register("confirmPassword")}
              />
              <button
                type="button"
                aria-label={showConfirm ? "Hide confirm password" : "Show confirm password"}
                onClick={() => setShowConfirm((prev) => !prev)}
                className="absolute right-1 top-[30px] inline-flex h-11 w-11 items-center justify-center rounded-lg text-muted hover:text-ink transition"
              >
                {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {serverError ? (
              <div
                className="rounded-xl border border-danger/40 bg-danger-soft px-3 py-2 text-sm text-danger-ink"
                role="alert"
              >
                {serverError}
              </div>
            ) : null}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Changing password…" : "Change password"}
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-muted">
          <Link className="inline-flex min-h-11 items-center px-3 font-semibold text-brand-700 hover:underline" to="/login">
            Back to sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
