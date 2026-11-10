"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";

interface MyStats {
  conversations: number;
  messages: number;
}

export default function ProfilePage() {
  const { user, refresh } = useAuth();

  const [fullName, setFullName] = useState("");
  const [profileNotice, setProfileNotice] = useState("");
  const [profileError, setProfileError] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordNotice, setPasswordNotice] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  const [stats, setStats] = useState<MyStats | null>(null);

  useEffect(() => {
    if (user) setFullName(user.full_name || "");
  }, [user]);

  useEffect(() => {
    api
      .get<MyStats>("/users/me/stats")
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    setSavingProfile(true);
    setProfileError("");
    setProfileNotice("");

    try {
      await api.put("/users/me", { full_name: fullName.trim() });
      await refresh();
      setProfileNotice("Profile updated.");
    } catch (err) {
      setProfileError(
        err instanceof ApiError ? err.message : "Could not update profile.",
      );
    } finally {
      setSavingProfile(false);
    }
  }

  async function changePassword(event: React.FormEvent) {
    event.preventDefault();
    setSavingPassword(true);
    setPasswordError("");
    setPasswordNotice("");

    try {
      await api.post("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordNotice("Password changed.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordError(
        err instanceof ApiError ? err.message : "Could not change password.",
      );
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <AppLayout title="Profile" subtitle="Manage your account details.">
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-5">
          <div className="card p-5">
            <h2 className="text-sm font-semibold text-slate-800">
              Account information
            </h2>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-500">Username</dt>
                <dd className="font-medium text-slate-800">
                  {user?.username}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Email</dt>
                <dd className="font-medium text-slate-800">{user?.email}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Role</dt>
                <dd>
                  <Badge tone={user?.role === "admin" ? "brand" : "neutral"}>
                    {user?.role}
                  </Badge>
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Joined</dt>
                <dd className="text-slate-700">
                  {formatDate(user?.created_at)}
                </dd>
              </div>
            </dl>
          </div>

          <form className="card p-5" onSubmit={saveProfile}>
            <h2 className="text-sm font-semibold text-slate-800">
              Update profile
            </h2>

            {profileNotice ? (
              <div className="mt-3">
                <Alert tone="success">{profileNotice}</Alert>
              </div>
            ) : null}
            {profileError ? (
              <div className="mt-3">
                <Alert tone="danger">{profileError}</Alert>
              </div>
            ) : null}

            <div className="mt-4">
              <label className="label" htmlFor="full-name">
                Full name
              </label>
              <input
                id="full-name"
                className="input"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn-primary mt-4"
              disabled={savingProfile}
            >
              {savingProfile ? <Spinner /> : null}
              Save changes
            </button>
          </form>
        </div>

        <div className="space-y-5">
          <div className="card grid grid-cols-2 gap-4 p-5">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Conversations
              </p>
              <p className="mt-1 text-2xl font-bold text-brand-600">
                {stats?.conversations ?? "—"}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Messages
              </p>
              <p className="mt-1 text-2xl font-bold text-brand-600">
                {stats?.messages ?? "—"}
              </p>
            </div>
          </div>

          <form className="card p-5" onSubmit={changePassword}>
            <h2 className="text-sm font-semibold text-slate-800">
              Change password
            </h2>

            {passwordNotice ? (
              <div className="mt-3">
                <Alert tone="success">{passwordNotice}</Alert>
              </div>
            ) : null}
            {passwordError ? (
              <div className="mt-3">
                <Alert tone="danger">{passwordError}</Alert>
              </div>
            ) : null}

            <div className="mt-4">
              <label className="label" htmlFor="current-password">
                Current password
              </label>
              <input
                id="current-password"
                type="password"
                className="input"
                required
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
              />
            </div>

            <div className="mt-3">
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
              />
            </div>

            <button
              type="submit"
              className="btn-primary mt-4"
              disabled={savingPassword}
            >
              {savingPassword ? <Spinner /> : null}
              Change password
            </button>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}
