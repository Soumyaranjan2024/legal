"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { truncate } from "@/lib/format";
import type { SearchFilterOptions, SearchResponse, SearchResult } from "@/lib/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("semantic");
  const [topK, setTopK] = useState(5);
  const [courtType, setCourtType] = useState("");
  const [courtTypes, setCourtTypes] = useState<string[]>([]);

  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<SearchFilterOptions>("/search/filters")
      .then((options) => setCourtTypes(options.court_types))
      .catch(() => setCourtTypes([]));
  }, []);

  async function runSearch(event: React.FormEvent) {
    event.preventDefault();

    if (query.trim().length < 2) {
      setError("Please enter at least 2 characters.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.post<SearchResponse>("/search", {
        query: query.trim(),
        mode,
        top_k: topK,
        court_type: courtType || null,
      });

      setResults(response.results);
      setSearched(true);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Search failed. Try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Legal Search"
      subtitle="Semantic and keyword search across Acts, sections and judgments."
    >
      <div className="space-y-6">
        <form className="card p-5" onSubmit={runSearch}>
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              className="input flex-1"
              placeholder="e.g. punishment for cheating under the IT Act"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button
              type="submit"
              className="btn-primary sm:w-32"
              disabled={loading}
            >
              {loading ? <Spinner /> : null}
              Search
            </button>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <label className="label" htmlFor="mode">
                Search mode
              </label>
              <select
                id="mode"
                className="input"
                value={mode}
                onChange={(event) => setMode(event.target.value)}
              >
                <option value="semantic">Semantic (embeddings)</option>
                <option value="keyword">Keyword (exact)</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>

            <div>
              <label className="label" htmlFor="court">
                Court filter
              </label>
              <select
                id="court"
                className="input"
                value={courtType}
                onChange={(event) => setCourtType(event.target.value)}
              >
                <option value="">All courts</option>
                {courtTypes.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label" htmlFor="topk">
                Results: {topK}
              </label>
              <input
                id="topk"
                type="range"
                min={1}
                max={20}
                value={topK}
                className="w-full"
                onChange={(event) => setTopK(Number(event.target.value))}
              />
            </div>
          </div>
        </form>

        {error ? <Alert tone="danger">{error}</Alert> : null}

        {loading ? (
          <div className="flex justify-center py-16 text-brand-600">
            <Spinner className="h-6 w-6" />
          </div>
        ) : null}

        {!loading && searched && results.length === 0 ? (
          <EmptyState
            icon="🔍"
            title="No matching legal text found"
            description="Try different keywords or switch the search mode."
          />
        ) : null}

        {!loading && results.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-slate-500">
              {results.length} result{results.length === 1 ? "" : "s"}
            </p>

            {results.map((result, index) => (
              <article key={index} className="card p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="brand">{result.source}</Badge>
                  {result.page ? (
                    <Badge tone="neutral">page {result.page}</Badge>
                  ) : null}
                  {result.court_name ? (
                    <Badge tone="neutral">{result.court_name}</Badge>
                  ) : null}
                  {typeof result.score === "number" ? (
                    <Badge tone="success">
                      score {result.score.toFixed(3)}
                    </Badge>
                  ) : null}
                  {result.source_url ? (
                    <a
                      href={result.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="ml-auto text-xs text-brand-600 hover:underline"
                    >
                      source link
                    </a>
                  ) : null}
                </div>

                <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                  {truncate(result.text, 600)}
                </p>

                {result.acts || result.sections ? (
                  <p className="mt-2 text-xs text-slate-400">
                    {result.acts ? `Acts: ${result.acts}` : ""}
                    {result.sections ? ` · Sections: ${result.sections}` : ""}
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        ) : null}
      </div>
    </AppLayout>
  );
}
