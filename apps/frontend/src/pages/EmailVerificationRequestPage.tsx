import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useSearchParams } from "react-router-dom";
import { z } from "zod";

import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { requestEmailVerification } from "../features/auth/auth-api";

const schema = z.object({
  email: z.string().email("Enter a valid email address.")
});
type FormValues = z.infer<typeof schema>;

export function EmailVerificationRequestPage() {
  const [params] = useSearchParams();
  const [sent, setSent] = useState(false);
  const [serverError, setServerError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: params.get("email") ?? "" }
  });

  const onSubmit = handleSubmit(async ({ email }) => {
    setServerError("");
    try {
      await requestEmailVerification(email);
      setSent(true);
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : "Request could not be completed."
      );
    }
  });

  return (
    <main className="subtle-grid flex min-h-screen items-center justify-center px-4 py-10">
      <section className="panel w-full max-w-md p-7 sm:p-8">
        <h1 className="text-2xl font-bold">Verify your email</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Request a fresh verification link. The response does not disclose
          whether an account exists or is already verified.
        </p>

        {sent ? (
          <div className="mt-6 rounded-xl border border-line bg-surface p-4 text-sm">
            If verification is required, instructions have been sent.
          </div>
        ) : (
          <form className="mt-7 space-y-4" onSubmit={onSubmit} noValidate>
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              error={errors.email?.message}
              {...register("email")}
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
              {isSubmitting ? "Submitting…" : "Send verification link"}
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-muted">
          <Link className="font-semibold text-brand-700 hover:underline" to="/login">
            Back to sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
