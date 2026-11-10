"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";
import { StatCard } from "@/components/ui/StatCard";
import { api } from "@/lib/api";
import type { AdminStats } from "@/lib/types";

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<AdminStats>("/admin/stats")
      .then(setStats)
      .catch(() => setError("Failed to load admin statistics."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppLayout
      title="Admin Overview"
      subtitle="System-wide statistics for the legal information platform."
      requireAdmin
    >
      {loading ? (
        <div className="flex justify-center py-20 text-brand-600">
          <Spinner className="h-6 w-6" />
        </div>
      ) : error ? (
        <Alert tone="danger">{error}</Alert>
      ) : stats ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total users" value={stats.total_users} />
            <StatCard
              label="Active users"
              value={stats.active_users}
              tone="emerald"
            />
            <StatCard
              label="Administrators"
              value={stats.admin_users}
              tone="violet"
            />
            <StatCard
              label="Conversations"
              value={stats.total_conversations}
              tone="amber"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard label="Documents" value={stats.total_documents} />
            <StatCard
              label="Chunks in ChromaDB"
              value={stats.total_chunks}
              tone="emerald"
            />
            <StatCard
              label="Chat messages"
              value={stats.total_messages}
              tone="amber"
            />
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-slate-800">
                Configuration
              </h2>
              <dl className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500">LLM</dt>
                  <dd className="font-medium text-slate-800">
                    {stats.llm_provider === "gemini"
                      ? "Gemini"
                      : stats.llm_provider === "groq"
                        ? "Groq"
                        : "Grok"}{" "}
                    ({stats.llm_model})
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Embeddings</dt>
                  <dd className="font-medium text-slate-800">
                    {stats.embedding_model}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">LLM API key</dt>
                  <dd
                    className={
                      stats.llm_configured
                        ? "font-medium text-emerald-600"
                        : "font-medium text-amber-600"
                    }
                  >
                    {stats.llm_configured ? "Configured" : "Not configured"}
                  </dd>
                </div>
              </dl>

              <div className="mt-4 flex flex-wrap gap-3">
                <Link href="/admin/users" className="btn-secondary">
                  Manage users
                </Link>
                <Link href="/admin/reports" className="btn-secondary">
                  View reports
                </Link>
              </div>
            </div>

            <div className="card p-5">
              <h2 className="text-sm font-semibold text-slate-800">
                ChromaDB collections
              </h2>
              <table className="mt-3 w-full text-sm">
                <thead className="text-left text-xs uppercase tracking-wide text-slate-400">
                  <tr>
                    <th className="pb-2">Collection</th>
                    <th className="pb-2 text-right">Records</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats.collections.map((collection) => (
                    <tr key={collection.name}>
                      <td className="py-2 font-medium text-slate-700">
                        {collection.name}
                      </td>
                      <td className="py-2 text-right text-slate-600">
                        {collection.count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </AppLayout>
  );
}
