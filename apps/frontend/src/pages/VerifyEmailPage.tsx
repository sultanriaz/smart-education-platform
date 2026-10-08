import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { confirmEmailVerification } from "../features/auth/auth-api";

type VerificationState = "working" | "success" | "error";

export function VerifyEmailPage() {
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

  const [state, setState] = useState<VerificationState>("working");
  const [message, setMessage] = useState("Verifying your email…");

  useEffect(() => {
    let cancelled = false;

    const verify = async () => {
      if (!token) {
        setState("error");
        setMessage("The verification link is incomplete.");
        return;
      }
      try {
        await confirmEmailVerification(token);
        if (!cancelled) {
          setState("success");
          setMessage("Your email address has been verified.");
        }
      } catch (error) {
        if (!cancelled) {
          setState("error");
          setMessage(
            error instanceof Error
              ? error.message
              : "The verification link is invalid or expired."
          );
        }
      }
    };

    void verify();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <main className="subtle-grid flex min-h-screen items-center justify-center px-4 py-10">
      <section className="panel w-full max-w-md p-7 sm:p-8">
        <h1 className="text-2xl font-bold">Email verification</h1>
        <div
          className={`mt-6 rounded-xl border p-4 text-sm ${
            state === "error"
              ? "border-red-200 bg-red-50 text-danger"
              : "border-line bg-surface"
          }`}
          role={state === "error" ? "alert" : undefined}
        >
          {message}
        </div>
        {state !== "working" ? (
          <p className="mt-6 text-center text-sm">
            <Link className="font-semibold text-brand-700 hover:underline" to="/login">
              Continue to sign in
            </Link>
          </p>
        ) : null}
      </section>
    </main>
  );
}
