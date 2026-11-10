"use client";

import { useCallback, useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Disclaimer } from "@/components/Disclaimer";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import type { Procedure } from "@/lib/types";

function ListBlock({ title, items }: { title: string; items: string[] }) {
  if (!items || items.length === 0) return null;

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {title}
      </p>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-slate-600">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ProceduresPage() {
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);

    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());

    try {
      const response = await api.get<{
        total: number;
        procedures: Procedure[];
      }>(`/procedures?${params.toString()}`);
      setProcedures(response.procedures);
    } catch {
      setProcedures([]);
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <AppLayout
      title="Legal Procedures"
      subtitle="Procedures, timelines, documents and forms extracted from the sources."
    >
      <div className="space-y-5">
        <div className="card p-4">
          <input
            className="input"
            placeholder="Search procedures, required documents or Acts…"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-16 text-brand-600">
            <Spinner className="h-6 w-6" />
          </div>
        ) : procedures.length === 0 ? (
          <EmptyState
            icon="🧾"
            title="No procedures available"
            description="Procedure details appear once documents describing them are ingested."
          />
        ) : (
          <div className="space-y-3">
            {procedures.map((procedure) => {
              const open = openId === procedure.document_id;

              return (
                <div key={procedure.document_id} className="card p-4">
                  <button
                    className="flex w-full items-start justify-between gap-3 text-left"
                    onClick={() =>
                      setOpenId(open ? null : procedure.document_id)
                    }
                  >
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">
                        {procedure.title || procedure.file_name}
                      </h3>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {procedure.legal_category ? (
                          <Badge tone="brand">{procedure.legal_category}</Badge>
                        ) : null}
                        {procedure.court_name ? (
                          <Badge tone="neutral">{procedure.court_name}</Badge>
                        ) : null}
                      </div>
                    </div>
                    <span className="text-slate-400">{open ? "−" : "+"}</span>
                  </button>

                  {open ? (
                    <div className="mt-4 space-y-3 border-t border-slate-100 pt-4">
                      {procedure.acts ? (
                        <p className="text-xs text-slate-500">
                          Acts: {procedure.acts}
                        </p>
                      ) : null}

                      <ListBlock
                        title="Legal procedure"
                        items={procedure.legal_procedure}
                      />
                      <ListBlock
                        title="Potentially required documents"
                        items={procedure.required_documents}
                      />
                      <ListBlock
                        title="Government forms"
                        items={procedure.government_forms}
                      />

                      {procedure.timeline ? (
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                            Timeline
                          </p>
                          <p className="mt-1 text-sm text-slate-600">
                            {procedure.timeline}
                          </p>
                        </div>
                      ) : null}

                      {procedure.source_url ? (
                        <a
                          className="text-xs text-brand-600 hover:underline"
                          href={procedure.source_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open source document
                        </a>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}

        <Disclaimer />
      </div>
    </AppLayout>
  );
}
