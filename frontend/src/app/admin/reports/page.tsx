"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { SystemReport } from "@/lib/types";

function Breakdown({
  title,
  data,
}: {
  title: string;
  data: Record<string, number>;
}) {
  const entries = Object.entries(data || {});

  return (
    <div className="card p-5">
      <h2 className="text-sm font-semibold text-slate-800">{title}</h2>

      {entries.length === 0 ? (
        <p className="mt-2 text-sm text-slate-400">No data available.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {entries.map(([label, value]) => (
            <li key={label} className="flex items-center justify-between text-sm">
              <span className="text-slate-600">{label}</span>
              <span className="font-semibold text-slate-800">{value}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AdminReportsPage() {
  const [report, setReport] = useState<SystemReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<SystemReport>("/admin/report")
      .then(setReport)
      .catch(() => setError("Failed to generate the report."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppLayout
      title="Reports"
      subtitle="Breakdown of the knowledge base and platform usage."
      requireAdmin
    >
      {loading ? (
        <div className="flex justify-center py-20 text-brand-600">
          <Spinner className="h-6 w-6" />
        </div>
      ) : error ? (
        <Alert tone="danger">{error}</Alert>
      ) : report ? (
        <div className="space-y-5">
          <div className="card p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-sm font-semibold text-slate-800">
                System report
              </h2>
              <span className="text-xs text-slate-400">
                Generated {formatDateTime(report.generated_at)}
              </span>
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
              {[
                { label: "Users", value: report.stats.total_users },
                { label: "Documents", value: report.stats.total_documents },
                { label: "Chunks", value: report.stats.total_chunks },
                {
                  label: "Conversations",
                  value: report.stats.total_conversations,
                },
                { label: "Messages", value: report.stats.total_messages },
                { label: "Admins", value: report.stats.admin_users },
              ].map((item) => (
                <div key={item.label}>
                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    {item.label}
                  </p>
                  <p className="mt-1 text-xl font-bold text-brand-600">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <Breakdown
              title="Documents by court type"
              data={report.documents_by_court_type}
            />
            <Breakdown
              title="Documents by category"
              data={report.documents_by_category}
            />
            <Breakdown title="Users by role" data={report.users_by_role} />
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-slate-800">
                Most referenced Acts
              </h2>
              {report.top_acts.length === 0 ? (
                <p className="mt-2 text-sm text-slate-400">
                  No Acts recorded yet.
                </p>
              ) : (
                <ul className="mt-3 space-y-2">
                  {report.top_acts.map((item) => (
                    <li
                      key={item.label}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-slate-600">{item.label}</span>
                      <span className="font-semibold text-slate-800">
                        {String(item.value)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </AppLayout>
  );
}
