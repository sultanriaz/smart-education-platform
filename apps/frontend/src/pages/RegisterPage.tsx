import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

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
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = handleSubmit(async (input) => {
    const values = { full_name: input.full_name, email: input.email, password: input.password };
    setServerError("");
    try {
      await registerAccount(values);

      // Registration integration should normally enqueue verification itself.
      // This generic call is safe and enumeration-resistant, and guarantees the
      // user can receive a link during a staged Sprint 18 merge.
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
    <main className="subtle-grid flex min-h-screen items-center justify-center px-4 py-10">
      <section className="panel w-full max-w-md p-7 sm:p-8">
        <h1 className="text-2xl font-bold">Create student account</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Public registration creates a Student account. Teacher and Admin accounts
          are provisioned by administrators.
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
          <Input
            label="Password"
            type="password"
            autoComplete="new-password"
            hint="12–128 characters with uppercase, lowercase, a number, and a symbol."
            error={errors.password?.message}
            {...register("password")}
          />
          <Input
            label="Confirm password"
            type="password"
            autoComplete="new-password"
            error={errors.confirmPassword?.message}
            {...register("confirmPassword")}
          />
          {serverError ? (
            <div
              className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-danger"
              role="alert"
            >
              {serverError}
            </div>
          ) : null}
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Creating account…" : "Create account"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already registered?{" "}
          <Link className="font-semibold text-brand-700 hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
