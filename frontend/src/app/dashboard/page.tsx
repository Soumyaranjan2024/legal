"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/AppLayout";
import { Disclaimer } from "@/components/Disclaimer";
import { StatCard } from "@/components/ui/StatCard";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api";
import { formatDateTime, truncate } from "@/lib/format";
import type { ConversationSummary, SystemStats } from "@/lib/types";

interface MyStats {
  conversations: number;
  messages: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [mine, setMine] = useState<MyStats | null>(null);
  const [recent, setRecent] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<SystemStats>("/system/stats").catch(() => null),
      api.get<MyStats>("/users/me/stats").catch(() => null),
      api
        .get<{ conversations: ConversationSummary[] }>("/chat/conversations")
        .catch(() => null),
    ])
      .then(([systemStats, myStats, conversations]) => {
        setStats(systemStats);
        setMine(myStats);
        setRecent(conversations?.conversations?.slice(0, 5) ?? []);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppLayout
      title="Dashboard"
      subtitle="Overview of the legal knowledge base and your activity."
    >
      {loading ? (
        <div className="flex justify-center py-20 text-brand-600">
          <Spinner className="h-6 w-6" />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Legal documents"
              value={stats?.documents ?? "—"}
              hint="Indexed in ChromaDB"
            />
            <StatCard
              label="Indexed chunks"
              value={stats?.chunks ?? "—"}
              tone="emerald"
              hint="Embedded with BGE/E5"
            />
            <StatCard
              label="Your conversations"
              value={mine?.conversations ?? "—"}
              tone="amber"
            />
            <StatCard
              label="Your messages"
              value={mine?.messages ?? "—"}
              tone="violet"
            />
          </div>

          <div className="card p-5">
            <h2 className="text-sm font-semibold text-slate-800">
              Quick actions
            </h2>
            <div className="mt-3 flex flex-wrap gap-3">
              <Link href="/chat" className="btn-primary">
                Ask the legal chatbot
              </Link>
              <Link href="/search" className="btn-secondary">
                Search the corpus
              </Link>
              <Link href="/cases" className="btn-secondary">
                Browse judgments
              </Link>
              <Link href="/documents" className="btn-secondary">
                Upload a document
              </Link>
            </div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-800">
                Recent conversations
              </h2>
              <Link
                href="/history"
                className="text-xs font-medium text-brand-600 hover:underline"
              >
                View all
              </Link>
            </div>

            <div className="mt-3">
              {recent.length === 0 ? (
                <EmptyState
                  icon="💬"
                  title="No conversations yet"
                  description="Start a chat to ask about Indian legal provisions."
                />
              ) : (
                <ul className="divide-y divide-slate-100">
                  {recent.map((conversation) => (
                    <li
                      key={conversation.conversation_id}
                      className="flex items-center justify-between gap-3 py-3"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-slate-800">
                          {conversation.title || "Untitled conversation"}
                        </p>
                        <p className="text-xs text-slate-400">
                          {conversation.message_count} messages ·{" "}
                          {formatDateTime(conversation.last_message_at)}
                        </p>
                      </div>
                      <Link
                        href="/history"
                        className="shrink-0 text-xs font-medium text-brand-600 hover:underline"
                      >
                        Open
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="text-sm font-semibold text-slate-800">
              System configuration
            </h2>
            <dl className="mt-3 grid gap-3 sm:grid-cols-3">
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-400">
                  Embedding model
                </dt>
                <dd className="mt-1 text-sm font-medium text-slate-700">
                  {stats?.embedding_model ?? "—"}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-400">
                  LLM
                </dt>
                <dd className="mt-1 text-sm font-medium text-slate-700">
                  {stats?.llm_provider === "gemini"
                    ? "Gemini"
                    : stats?.llm_provider === "groq"
                      ? "Groq"
                      : stats?.llm_provider === "grok"
                        ? "Grok (xAI)"
                        : "Not configured"}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-400">
                  LLM status
                </dt>
                <dd className="mt-1 text-sm font-medium">
                  {stats?.llm_configured ? (
                    <span className="text-emerald-600">Configured</span>
                  ) : (
                    <span className="text-amber-600">API key not set</span>
                  )}
                </dd>
              </div>
            </dl>
          </div>

          <Disclaimer />
        </div>
      )}
    </AppLayout>
  );
}
