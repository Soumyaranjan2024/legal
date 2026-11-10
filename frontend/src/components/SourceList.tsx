import type { LegalSource } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

export function SourceList({ sources }: { sources: LegalSource[] }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Sources
      </p>
      <ul className="space-y-1.5">
        {sources.map((source, index) => (
          <li
            key={`${source.document_id ?? source.document}-${index}`}
            className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs"
          >
            <span className="font-medium text-slate-700">
              {source.document || "Unknown document"}
            </span>

            {source.page ? <Badge tone="neutral">page {source.page}</Badge> : null}

            {source.court_name ? (
              <Badge tone="brand">{source.court_name}</Badge>
            ) : null}

            {source.court_type ? (
              <Badge tone="neutral">{source.court_type}</Badge>
            ) : null}

            {source.source_url ? (
              <a
                className="text-brand-600 hover:underline"
                href={source.source_url}
                target="_blank"
                rel="noreferrer"
              >
                source link
              </a>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
