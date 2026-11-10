"use client";

import { useCallback, useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { DocumentSummary, UploadResponse } from "@/lib/types";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [file, setFile] = useState<File | null>(null);
  const [sourceUrl, setSourceUrl] = useState("");
  const [uploading, setUploading] = useState(false);

  const [ingestUrl, setIngestUrl] = useState("");
  const [ingestingUrl, setIngestingUrl] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);

    try {
      const response = await api.get<{
        total: number;
        documents: DocumentSummary[];
      }>("/documents");
      setDocuments(response.documents);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleUpload(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!file) {
      setError("Please choose a PDF file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    if (sourceUrl.trim()) formData.append("source_url", sourceUrl.trim());

    setUploading(true);

    try {
      const result = await api.upload<UploadResponse>("/documents/upload", formData);
      setNotice(
        `Ingested "${result.file_name}" — ${result.total_chunks} chunks` +
          (result.ocr_used ? " (OCR used)" : "") +
          ".",
      );
      setFile(null);
      setSourceUrl("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleIngestUrl(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!ingestUrl.trim()) return;

    setIngestingUrl(true);

    try {
      const result = await api.post<UploadResponse>("/documents/ingest-url", {
        url: ingestUrl.trim(),
      });
      setNotice(
        `Downloaded and ingested "${result.file_name}" — ${result.total_chunks} chunks.`,
      );
      setIngestUrl("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "URL ingestion failed.");
    } finally {
      setIngestingUrl(false);
    }
  }

  async function handleDelete(documentId: string) {
    if (!window.confirm("Delete this document and all of its chunks?")) return;

    try {
      await api.del(`/documents/${documentId}`);
      setNotice("Document deleted.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  return (
    <AppLayout
      title="Documents & Uploads"
      subtitle="Upload PDFs and manage the documents stored in ChromaDB."
    >
      <div className="space-y-6">
        {error ? <Alert tone="danger">{error}</Alert> : null}
        {notice ? <Alert tone="success">{notice}</Alert> : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <form className="card p-5" onSubmit={handleUpload}>
            <h2 className="text-sm font-semibold text-slate-800">
              Upload a PDF
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              The document is text-extracted, OCR-processed if scanned,
              chunked, embedded and stored in ChromaDB.
            </p>

            <div className="mt-4">
              <label className="label" htmlFor="file">
                PDF file
              </label>
              <input
                id="file"
                type="file"
                accept="application/pdf"
                className="input"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </div>

            <div className="mt-3">
              <label className="label" htmlFor="source-url">
                Source URL (optional)
              </label>
              <input
                id="source-url"
                className="input"
                placeholder="https://www.indiacode.nic.in/…"
                value={sourceUrl}
                onChange={(event) => setSourceUrl(event.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn-primary mt-4 w-full"
              disabled={uploading}
            >
              {uploading ? <Spinner /> : null}
              {uploading ? "Processing…" : "Upload & ingest"}
            </button>
          </form>

          <form className="card p-5" onSubmit={handleIngestUrl}>
            <h2 className="text-sm font-semibold text-slate-800">
              Ingest from an official source URL
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Download a publicly accessible PDF from India Code, the Supreme
              Court, a High Court or eCourts and ingest it.
            </p>

            <div className="mt-4">
              <label className="label" htmlFor="ingest-url">
                PDF URL
              </label>
              <input
                id="ingest-url"
                className="input"
                placeholder="https://…/judgment.pdf"
                value={ingestUrl}
                onChange={(event) => setIngestUrl(event.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn-secondary mt-4 w-full"
              disabled={ingestingUrl}
            >
              {ingestingUrl ? <Spinner /> : null}
              {ingestingUrl ? "Downloading…" : "Download & ingest"}
            </button>

            <p className="mt-3 text-xs text-slate-400">
              Only publicly accessible documents are supported. Restricted
              content and CAPTCHA-protected pages are not bypassed.
            </p>
          </form>
        </div>

        <div className="card overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
            <h2 className="text-sm font-semibold text-slate-800">
              Ingested documents
            </h2>
            <span className="text-xs text-slate-500">
              {documents.length} document(s)
            </span>
          </div>

          {loading ? (
            <div className="flex justify-center py-12 text-brand-600">
              <Spinner className="h-6 w-6" />
            </div>
          ) : documents.length === 0 ? (
            <div className="p-5">
              <EmptyState
                icon="📁"
                title="No documents yet"
                description="Upload a PDF above to build the legal knowledge base."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3">Document</th>
                    <th className="px-5 py-3">Court</th>
                    <th className="px-5 py-3">Chunks</th>
                    <th className="px-5 py-3">OCR</th>
                    <th className="px-5 py-3">Ingested</th>
                    <th className="px-5 py-3" />
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
                          {document.file_name}
                        </p>
                      </td>
                      <td className="px-5 py-3 text-slate-600">
                        {document.court_type || "—"}
                      </td>
                      <td className="px-5 py-3 text-slate-600">
                        {document.chunk_count}
                      </td>
                      <td className="px-5 py-3">
                        <Badge tone={document.ocr_used ? "warning" : "neutral"}>
                          {document.ocr_used ? "yes" : "no"}
                        </Badge>
                      </td>
                      <td className="px-5 py-3 text-xs text-slate-500">
                        {formatDateTime(document.ingested_at)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          className="text-xs font-medium text-red-600 hover:underline"
                          onClick={() => handleDelete(document.document_id)}
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
