"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { PublicNav } from "@/components/PublicNav";
import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";

interface ForgotResponse {
  detail: string;
  reset_token?: string | null;
}

export default function ForgotPasswordPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [step, setStep] = useState<"request" | "reset">("request");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function requestToken(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setSubmitting(true);

    try {
      const result = await api.post<ForgotResponse>("/auth/forgot-password", {
        email: email.trim(),
      });

      setMessage(result.detail);

      if (result.reset_token) {
        setToken(result.reset_token);
        setStep("reset");
      }
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Unable to process the request.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function resetPassword(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setSubmitting(true);

    try {
      const result = await api.post<{ detail: string }>(
        "/auth/reset-password",
        { token: token.trim(), new_password: newPassword },
      );
      setMessage(`${result.detail} Redirecting to login…`);
      setTimeout(() => router.push("/login"), 1200);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Unable to reset the password.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen">
      <PublicNav />
      <div className="mx-auto flex max-w-md flex-col px-4 py-16">
        <div className="card p-6">
          <h1 className="text-xl font-bold text-slate-900">Reset password</h1>
          <p className="mt-1 text-sm text-slate-500">
            {step === "request"
              ? "Enter your email to receive a reset token."
              : "Paste your reset token and choose a new password."}
          </p>

          {message ? (
            <div className="mt-4">
              <Alert tone="success">{message}</Alert>
            </div>
          ) : null}

          {error ? (
            <div className="mt-4">
              <Alert tone="danger">{error}</Alert>
            </div>
          ) : null}

          {step === "request" ? (
            <form className="mt-5 space-y-4" onSubmit={requestToken}>
              <div>
                <label className="label" htmlFor="email">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  className="input"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                />
              </div>
              <button
                type="submit"
                className="btn-primary w-full"
                disabled={submitting}
              >
                {submitting ? <Spinner /> : null}
                Send reset token
              </button>
            </form>
          ) : (
            <form className="mt-5 space-y-4" onSubmit={resetPassword}>
              <div>
                <label className="label" htmlFor="token">
                  Reset token
                </label>
                <input
                  id="token"
                  className="input font-mono text-xs"
                  required
                  value={token}
                  onChange={(event) => setToken(event.target.value)}
                />
              </div>
              <div>
                <label className="label" htmlFor="new-password">
                  New password
                </label>
                <input
                  id="new-password"
                  type="password"
                  className="input"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  placeholder="At least 8 characters"
                />
              </div>
              <button
                type="submit"
                className="btn-primary w-full"
                disabled={submitting}
              >
                {submitting ? <Spinner /> : null}
                Set new password
              </button>
            </form>
          )}

          <p className="mt-5 text-center text-sm text-slate-500">
            <Link href="/login" className="text-brand-600 hover:underline">
              Back to login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
