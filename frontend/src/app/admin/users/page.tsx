"use client";

import { useCallback, useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { UserPublic } from "@/lib/types";

export default function AdminUsersPage() {
  const { user: currentUser } = useAuth();

  const [users, setUsers] = useState<UserPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);

    try {
      const response = await api.get<{ total: number; users: UserPublic[] }>(
        "/admin/users",
      );
      setUsers(response.users);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function updateUser(userId: string, payload: Record<string, unknown>) {
    setError("");
    setNotice("");

    try {
      await api.patch(`/admin/users/${userId}`, payload);
      setNotice("User updated.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Update failed.");
    }
  }

  async function deleteUser(userId: string) {
    if (!window.confirm("Delete this user account?")) return;

    setError("");
    setNotice("");

    try {
      await api.del(`/admin/users/${userId}`);
      setNotice("User deleted.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  return (
    <AppLayout
      title="User Management"
      subtitle="Manage user roles and account status."
      requireAdmin
    >
      <div className="space-y-4">
        {error ? <Alert tone="danger">{error}</Alert> : null}
        {notice ? <Alert tone="success">{notice}</Alert> : null}

        <div className="card overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
            <h2 className="text-sm font-semibold text-slate-800">Users</h2>
            <span className="text-xs text-slate-500">{users.length} total</span>
          </div>

          {loading ? (
            <div className="flex justify-center py-12 text-brand-600">
              <Spinner className="h-6 w-6" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3">User</th>
                    <th className="px-5 py-3">Role</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">Joined</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((item) => {
                    const isSelf = item.user_id === currentUser?.user_id;

                    return (
                      <tr key={item.user_id} className="hover:bg-slate-50">
                        <td className="px-5 py-3">
                          <p className="font-medium text-slate-800">
                            {item.full_name || item.username}
                          </p>
                          <p className="text-xs text-slate-400">{item.email}</p>
                        </td>
                        <td className="px-5 py-3">
                          <select
                            className="rounded-md border border-slate-300 px-2 py-1 text-xs"
                            value={item.role}
                            disabled={isSelf}
                            onChange={(event) =>
                              updateUser(item.user_id, {
                                role: event.target.value,
                              })
                            }
                          >
                            <option value="user">user</option>
                            <option value="admin">admin</option>
                          </select>
                        </td>
                        <td className="px-5 py-3">
                          <Badge
                            tone={item.is_active ? "success" : "danger"}
                          >
                            {item.is_active ? "active" : "inactive"}
                          </Badge>
                        </td>
                        <td className="px-5 py-3 text-xs text-slate-500">
                          {formatDate(item.created_at)}
                        </td>
                        <td className="px-5 py-3 text-right">
                          <button
                            className="mr-3 text-xs font-medium text-brand-600 hover:underline"
                            disabled={isSelf}
                            onClick={() =>
                              updateUser(item.user_id, {
                                is_active: !item.is_active,
                              })
                            }
                          >
                            {item.is_active ? "Deactivate" : "Activate"}
                          </button>
                          <button
                            className="text-xs font-medium text-red-600 hover:underline disabled:text-slate-300"
                            disabled={isSelf}
                            onClick={() => deleteUser(item.user_id)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
