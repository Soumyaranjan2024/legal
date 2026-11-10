"use client";

import { useCallback, useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { DocumentSummary } from "@/lib/types";

interface RebuildResult {
  detail: string;
  ingested: number;
  failed: number;
  errors: { file: string; error: string }[];
}

export default function AdminDatasetsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);

    try {
      const response = await api.get<{
        total: number;
        documents: DocumentSummary[];
      }>("/admin/datasets");
      setDocuments(response.documents);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load datasets.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function rebuild() {
    if (
      !window.confirm(
        "Re-ingest every PDF in the dataset folder? This re-runs OCR, extraction and embeddings.",
      )
    ) {
      return;
    }

    setRebuilding(true);
    setError("");
    setNotice("");

    try {
      const result = await api.post<RebuildResult>("/admin/datasets/rebuild");
      setNotice(
        `Rebuild complete — ${result.ingested} ingested, ${result.failed} failed.`,
      );
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Rebuild failed.");
    } finally {
      setRebuilding(false);
    }
  }

  async function remove(documentId: string) {
    if (!window.confirm("Delete this dataset entry and its chunks?")) return;

    try {
      await api.del(`/documents/${documentId}`);
      setNotice("Document removed.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  return (
    <AppLayout
      title="Datasets"
      subtitle="Manage the legal documents that make up the knowledge base."
      requireAdmin
    >
      <div className="space-y-4">
        {error ? <Alert tone="danger">{error}</Alert> : null}
        {notice ? <Alert tone="success">{notice}</Alert> : null}

        <div className="card flex flex-wrap items-center justify-between gap-3 p-5">
          <div>
            <h2 className="text-sm font-semibold text-slate-800">
              Knowledge base
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              {documents.length} documents ·{" "}
              {documents.reduce((total, item) => total + item.chunk_count, 0)}{" "}
              chunks
            </p>
          </div>
          <button
            className="btn-primary"
            onClick={rebuild}
            disabled={rebuilding}
          >
            {rebuilding ? <Spinner /> : null}
            {rebuilding ? "Rebuilding…" : "Rebuild from dataset folder"}
          </button>
        </div>

        <div className="card overflow-hidden">
          {loading ? (
            <div className="flex justify-center py-12 text-brand-600">
              <Spinner className="h-6 w-6" />
            </div>
          ) : documents.length === 0 ? (
            <div className="p-5">
              <EmptyState
                icon="🗄"
                title="No datasets ingested"
                description="Upload PDFs on the Documents page or run a rebuild."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3">Document</th>
                    <th className="px-5 py-3">Source type</th>
                    <th className="px-5 py-3">Category</th>
                    <th className="px-5 py-3">Chunks</th>
                    <th className="px-5 py-3">Ingested</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {documents.map((document) => (
                    <tr key={document.document_id} className="hover:bg-slate-50">
                      <td className="px-5 py-3">
                        <p className="font-medium text-slate-800">
                          {document.title || document.file_name}
                        </p>
                        <p className="text-xs text-slate-400">
                          {document.document_id}
                        </p>
                      </td>
                      <td className="px-5 py-3">
                        <Badge tone="neutral">{document.source_type || "—"}</Badge>
                      </td>
                      <td className="px-5 py-3 text-slate-600">
                        {document.legal_category || "—"}
                      </td>
                      <td className="px-5 py-3 text-slate-600">
                        {document.chunk_count}
                      </td>
                      <td className="px-5 py-3 text-xs text-slate-500">
                        {formatDateTime(document.ingested_at)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          className="text-xs font-medium text-red-600 hover:underline"
                          onClick={() => remove(document.document_id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
