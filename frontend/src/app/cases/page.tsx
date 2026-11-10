"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/AppLayout";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { CaseFilterOptions, CaseSummary } from "@/lib/types";

export default function CasesPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [filters, setFilters] = useState<CaseFilterOptions>({
    court_types: [],
    categories: [],
  });
  const [courtType, setCourtType] = useState("");
  const [category, setCategory] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<CaseFilterOptions>("/cases/filters")
      .then(setFilters)
      .catch(() => setFilters({ court_types: [], categories: [] }));
  }, []);

  const load = useCallback(async () => {
    setLoading(true);

    const params = new URLSearchParams();

    if (courtType) params.set("court_type", courtType);
    if (category) params.set("category", category);
    if (query.trim()) params.set("q", query.trim());

    try {
      const response = await api.get<{ total: number; cases: CaseSummary[] }>(
        `/cases?${params.toString()}`,
      );
      setCases(response.cases);
    } catch {
      setCases([]);
    } finally {
      setLoading(false);
    }
  }, [courtType, category, query]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <AppLayout
      title="Cases & Judgments"
      subtitle="Supreme Court and High Court judgments with extracted legal details."
    >
      <div className="space-y-5">
        <div className="card grid gap-4 p-4 sm:grid-cols-3">
          <div>
            <label className="label" htmlFor="q">
              Search
            </label>
            <input
              id="q"
              className="input"
              placeholder="Case name, number or Act"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>

          <div>
            <label className="label" htmlFor="court">
              Court type
            </label>
            <select
              id="court"
              className="input"
              value={courtType}
              onChange={(event) => setCourtType(event.target.value)}
            >
              <option value="">All courts</option>
              {filters.court_types.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label" htmlFor="category">
              Legal category
            </label>
            <select
              id="category"
              className="input"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              <option value="">All categories</option>
              {filters.categories.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16 text-brand-600">
            <Spinner className="h-6 w-6" />
          </div>
        ) : cases.length === 0 ? (
          <EmptyState
            icon="⚖"
            title="No judgments found"
            description="Upload judgment PDFs or adjust the filters to see cases here."
          />
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-slate-500">{cases.length} case(s)</p>

            {cases.map((item) => (
              <Link
                key={item.document_id}
                href={`/cases/${item.document_id}`}
                className="card block p-4 transition hover:border-brand-300 hover:shadow-md"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-slate-900">
                    {item.case_name || item.file_name}
                  </h3>
                  {item.court_type ? (
                    <Badge tone="brand">{item.court_type}</Badge>
                  ) : null}
                  {item.legal_category ? (
                    <Badge tone="neutral">{item.legal_category}</Badge>
                  ) : null}
                </div>

                <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-500">
                  {item.case_number ? <span>No: {item.case_number}</span> : null}
                  {item.court_name ? <span>{item.court_name}</span> : null}
                  {item.judgment_date ? (
                    <span>Decided: {formatDate(item.judgment_date)}</span>
                  ) : null}
                </div>

                {item.acts ? (
                  <p className="mt-2 text-xs text-slate-400">
                    Acts: {item.acts}
                  </p>
                ) : null}
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
