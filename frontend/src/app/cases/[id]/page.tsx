"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/AppLayout";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import { formatDate, splitList } from "@/lib/format";
import type { CaseDetail } from "@/lib/types";

function Section({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  if (!items || items.length === 0) return null;

  return (
    <div className="card p-4">
      <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function CaseDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<CaseDetail>(`/cases/${params.id}`)
      .then(setCaseData)
      .catch(() =>
        setError("Could not load this case. It may have been removed."),
      )
      .finally(() => setLoading(false));
  }, [params.id]);

  return (
    <AppLayout title="Case Details" subtitle="Extracted judgment information.">
      <div className="space-y-5">
        <Link href="/cases" className="text-sm text-brand-600 hover:underline">
          ← Back to cases
        </Link>

        {loading ? (
          <div className="flex justify-center py-16 text-brand-600">
            <Spinner className="h-6 w-6" />
          </div>
        ) : error ? (
          <Alert tone="danger">{error}</Alert>
        ) : caseData ? (
          <>
            <div className="card p-5">
              <h1 className="text-lg font-bold text-slate-900">
                {caseData.case_name || caseData.file_name}
              </h1>

              <div className="mt-2 flex flex-wrap gap-2">
                {caseData.court_type ? (
                  <Badge tone="brand">{caseData.court_type}</Badge>
                ) : null}
                {caseData.legal_category ? (
                  <Badge tone="neutral">{caseData.legal_category}</Badge>
                ) : null}
                {caseData.case_number ? (
                  <Badge tone="neutral">No: {caseData.case_number}</Badge>
                ) : null}
              </div>

              <dl className="mt-4 grid gap-3 sm:grid-cols-3">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-400">
                    Court
                  </dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {caseData.court_name || "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-400">
                    Judgment date
                  </dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {caseData.judgment_date
                      ? formatDate(caseData.judgment_date)
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-400">
                    Source
                  </dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {caseData.source_url ? (
                      <a
                        className="text-brand-600 hover:underline"
                        href={caseData.source_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open source
                      </a>
                    ) : (
                      caseData.file_name || "—"
                    )}
                  </dd>
                </div>
              </dl>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="card p-4">
                <h2 className="text-sm font-semibold text-slate-800">
                  Applicable Acts
                </h2>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
                  {splitList(caseData.acts).length ? (
                    splitList(caseData.acts).map((act, index) => (
                      <li key={index}>{act}</li>
                    ))
                  ) : (
                    <li className="list-none text-slate-400">
                      Not available in the source document.
                    </li>
                  )}
                </ul>
              </div>

              <div className="card p-4">
                <h2 className="text-sm font-semibold text-slate-800">
                  Applicable Sections
                </h2>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
                  {splitList(caseData.sections).length ? (
                    splitList(caseData.sections).map((section, index) => (
                      <li key={index}>{section}</li>
                    ))
                  ) : (
                    <li className="list-none text-slate-400">
                      Not available in the source document.
                    </li>
                  )}
                </ul>
              </div>
            </div>

            <Section
              title="Important findings"
              items={caseData.important_findings}
            />
            <Section
              title="Legal procedure"
              items={caseData.legal_procedure}
            />
            <Section
              title="Potentially required documents"
              items={caseData.required_documents}
            />
            <Section
              title="Government forms"
              items={caseData.government_forms}
            />
            <Section
              title="Source references"
              items={caseData.source_references}
            />

            {caseData.timeline ? (
              <div className="card p-4">
                <h2 className="text-sm font-semibold text-slate-800">
                  Timeline
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  {caseData.timeline}
                </p>
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </AppLayout>
  );
}
