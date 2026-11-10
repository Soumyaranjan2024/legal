"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Markdown } from "@/components/Markdown";
import { SourceList } from "@/components/SourceList";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import type {
  ChatResponse,
  LegalSource,
  MessagePublic,
} from "@/lib/types";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: LegalSource[];
}

const SUGGESTIONS = [
  "What are the grounds for divorce under the Hindu Marriage Act?",
  "Explain the punishment for cruelty under the IT Act, 2000.",
  "What documents are required to file a dowry harassment complaint?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const params = new URLSearchParams(window.location.search);
    const existing = params.get("conversation");

    if (!existing) return;

    api
      .get<{ conversation_id: string; messages: MessagePublic[] }>(
        `/chat/conversations/${existing}`,
      )
      .then((data) => {
        setConversationId(data.conversation_id);
        setMessages(
          data.messages.map((message) => ({
            role: message.role === "assistant" ? "assistant" : "user",
            content: message.content,
            sources: message.sources,
          })),
        );
      })
      .catch(() => setError("Could not load that conversation."));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const send = useCallback(
    async (question: string) => {
      const trimmed = question.trim();

      if (!trimmed || sending) return;

      setError("");
      setMessages((current) => [...current, { role: "user", content: trimmed }]);
      setInput("");
      setSending(true);

      try {
        const response = await api.post<ChatResponse>("/chat", {
          question: trimmed,
          conversation_id: conversationId,
        });

        setConversationId(response.conversation_id);
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: response.answer,
            sources: response.sources,
          },
        ]);
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : "The chatbot could not answer right now.",
        );
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              "Sorry — I could not generate an answer. Please verify the LLM API key is configured and try again.",
          },
        ]);
      } finally {
        setSending(false);
      }
    },
    [conversationId, sending],
  );

  const autoAsked = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined" || autoAsked.current) return;

    const params = new URLSearchParams(window.location.search);
    const preset = params.get("q");

    if (!preset) return;

    autoAsked.current = true;
    send(preset);
  }, [send]);

  function startNewChat() {
    setMessages([]);
    setConversationId(null);
    setError("");
  }

  return (
    <AppLayout
      title="AI Legal Chatbot"
      subtitle="Ask a legal question and get the applicable law, the documents you need, the step-by-step procedure and the court to approach."
    >
      <div className="mx-auto max-w-3xl">
        <div className="card flex h-[75vh] flex-col">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-800">
                Conversation
              </span>
              {conversationId ? (
                <Badge tone="brand">saved</Badge>
              ) : (
                <Badge tone="neutral">new</Badge>
              )}
            </div>
            <button className="btn-secondary" onClick={startNewChat}>
              New chat
            </button>
          </div>

          <div className="scrollbar-thin flex-1 space-y-4 overflow-y-auto p-4">
            {messages.length === 0 && !sending ? (
              <div className="mx-auto max-w-lg py-10 text-center">
                <div className="text-3xl" aria-hidden>
                  ⚖
                </div>
                <p className="mt-3 text-base font-semibold text-slate-800">
                  Ask about Indian Acts, sections, procedures or judgments
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Answers are grounded in retrieved legal documents and always
                  include their sources.
                </p>
                <div className="mt-5 space-y-2">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-sm text-slate-600 hover:border-brand-300 hover:bg-brand-50"
                      onClick={() => send(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            {messages.map((message, index) => (
              <div
                key={index}
                className={
                  message.role === "user"
                    ? "flex justify-end"
                    : "flex justify-start"
                }
              >
                <div
                  className={
                    message.role === "user"
                      ? "max-w-[85%] rounded-2xl rounded-br-sm bg-brand-600 px-4 py-2.5 text-sm text-white"
                      : "max-w-[90%] rounded-2xl rounded-bl-sm border border-slate-200 bg-slate-50 px-4 py-3 text-sm"
                  }
                >
                  {message.role === "assistant" ? (
                    <>
                      <Markdown content={message.content} />
                      <SourceList sources={message.sources ?? []} />
                    </>
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              </div>
            ))}

            {sending ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Spinner />
                Retrieving relevant legal provisions and generating an answer…
              </div>
            ) : null}

            <div ref={bottomRef} />
          </div>

          {error ? (
            <div className="px-4 pb-2">
              <Alert tone="danger">{error}</Alert>
            </div>
          ) : null}

          <form
            className="border-t border-slate-200 p-3"
            onSubmit={(event) => {
              event.preventDefault();
              send(input);
            }}
          >
            <div className="flex items-end gap-2">
              <textarea
                className="input max-h-32 min-h-[44px] flex-1 resize-y"
                rows={1}
                value={input}
                placeholder="Type your legal question…"
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    send(input);
                  }
                }}
              />
              <button
                type="submit"
                className="btn-primary h-[44px]"
                disabled={sending || !input.trim()}
              >
                Send
              </button>
            </div>
          </form>
        </div>

        <p className="mt-3 text-center text-xs text-amber-900">
          Legal information only — not professional legal advice.
        </p>
      </div>
    </AppLayout>
  );
}
