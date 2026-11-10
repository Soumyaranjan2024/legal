"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PublicNav } from "@/components/PublicNav";
import { Disclaimer } from "@/components/Disclaimer";
import { api } from "@/lib/api";
import type { SystemStats } from "@/lib/types";

const FEATURES = [
  {
    icon: "💬",
    title: "AI Legal Chatbot",
    text: "Ask legal questions in plain language and receive source-grounded answers grounded in retrieved Indian legal documents.",
  },
  {
    icon: "🔍",
    title: "Semantic + Keyword Search",
    text: "Search across Indian Acts, sections and judgments using BGE/E5 embeddings stored in ChromaDB, or fall back to exact keyword matching.",
  },
  {
    icon: "⚖",
    title: "Judgments & Case Details",
    text: "Explore Supreme Court and High Court judgments with extracted findings, applicable Acts and source references.",
  },
  {
    icon: "🧾",
    title: "Procedures & Documents",
    text: "Understand legal procedures, timelines, potentially required documents and government forms extracted from official sources.",
  },
];

export default function HomePage() {
  const [stats, setStats] = useState<SystemStats | null>(null);

  useEffect(() => {
    api
      .get<SystemStats>("/system/stats")
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  return (
    <div className="min-h-screen">
      <PublicNav />

      <section className="bg-gradient-to-b from-white to-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-16 lg:px-8 lg:py-24">
          <div className="max-w-3xl">
            <span className="badge bg-brand-50 text-brand-700">
              Retrieval-Augmented Generation · ChromaDB
            </span>
            <h1 className="mt-4 text-3xl font-extrabold leading-tight text-slate-900 sm:text-4xl lg:text-5xl">
              Understand Indian law with an AI-powered legal information
              platform
            </h1>
            <p className="mt-4 text-base text-slate-600">
              Search Acts and sections, retrieve Supreme Court and High Court
              judgments, and ask legal questions through a RAG chatbot that
              always cites its sources.
            </p>

            <form
              action="/chat"
              method="get"
              className="mt-8 flex flex-col gap-3 sm:flex-row"
            >
              <input
                name="q"
                aria-label="Ask a legal question"
                className="input flex-1"
                placeholder="Ask a legal question, e.g. What are the grounds for divorce under the Hindu Marriage Act?"
              />
              <button type="submit" className="btn-primary px-6 py-3">
                Get answer
              </button>
            </form>
            <p className="mt-2 text-xs text-slate-500">
              No sign-up needed — ask directly and get a source-grounded answer.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/search" className="btn-secondary px-5 py-2.5">
                Search Acts &amp; sections
              </Link>
              <Link href="/cases" className="btn-secondary px-5 py-2.5">
                Browse judgments
              </Link>
              <Link href="/procedures" className="btn-secondary px-5 py-2.5">
                Legal procedures
              </Link>
            </div>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Legal documents", value: stats?.documents },
              { label: "Indexed chunks", value: stats?.chunks },
              { label: "Distinct sources", value: stats?.sources },
              { label: "Embedding model", value: null, text: stats?.embedding_model },
            ].map((item, index) => (
              <div key={index} className="card p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {item.label}
                </p>
                <p className="mt-2 text-lg font-bold text-brand-600">
                  {item.text ?? (item.value ?? "—")}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900">
          Everything in one legal workspace
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Built on FastAPI, Next.js, BGE/E5 embeddings and ChromaDB — with no
          external relational database.
        </p>

        <div className="mt-8 grid gap-5 sm:grid-cols-2">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="card p-6">
              <div className="text-2xl" aria-hidden>
                {feature.icon}
              </div>
              <h3 className="mt-3 text-lg font-semibold text-slate-900">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm text-slate-600">{feature.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-16 lg:px-8">
        <Disclaimer />
      </section>

      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="mx-auto max-w-6xl px-4 text-center text-xs text-slate-400 lg:px-8">
          Legal Information Retrieval System · Academic project · ChromaDB,
          BGE/E5 embeddings
        </div>
      </footer>
    </div>
  );
}
