"use client";

import { useCallback, useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Markdown } from "@/components/Markdown";
import { SourceList } from "@/components/SourceList";
import { Alert } from "@/components/ui/Alert";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError, api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { ConversationSummary, MessagePublic } from "@/lib/types";

export default function HistoryPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessagePublic[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState("");

  const loadConversations = useCallback(async () => {
    setLoadingList(true);

    try {
      const response = await api.get<{
        total: number;
        conversations: ConversationSummary[];
      }>("/chat/conversations");
      setConversations(response.conversations);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load conversations.",
      );
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  async function openConversation(conversationId: string) {
    setSelected(conversationId);
    setLoadingMessages(true);
    setError("");

    try {
      const response = await api.get<{
        conversation_id: string;
        messages: MessagePublic[];
      }>(`/chat/conversations/${conversationId}`);
      setMessages(response.messages);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load messages.");
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }

  async function deleteConversation(conversationId: string) {
    if (!window.confirm("Delete this conversation?")) return;

    try {
      await api.del(`/chat/conversations/${conversationId}`);
      if (selected === conversationId) {
        setSelected(null);
        setMessages([]);
      }
      await loadConversations();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    }
  }

  async function clearAll() {
    if (!window.confirm("Clear your entire chat history?")) return;

    try {
      await api.del("/chat/history");
      setSelected(null);
      setMessages([]);
      await loadConversations();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to clear history.");
    }
  }

  return (
    <AppLayout
      title="Chat History"
      subtitle="Review your previous legal questions and the answers you received."
    >
      <div className="space-y-4">
        {error ? <Alert tone="danger">{error}</Alert> : null}

        <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
          <div className="card overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-800">
                Conversations
              </h2>
              {conversations.length > 0 ? (
                <button
                  className="text-xs font-medium text-red-600 hover:underline"
                  onClick={clearAll}
                >
                  Clear all
                </button>
              ) : null}
            </div>

            {loadingList ? (
              <div className="flex justify-center py-10 text-brand-600">
                <Spinner className="h-5 w-5" />
              </div>
            ) : conversations.length === 0 ? (
              <div className="p-4">
                <EmptyState
                  icon="🕘"
                  title="No conversations"
                  description="Your chatbot conversations will appear here."
                />
              </div>
            ) : (
              <ul className="max-h-[65vh] divide-y divide-slate-100 overflow-y-auto scrollbar-thin">
                {conversations.map((conversation) => (
                  <li key={conversation.conversation_id}>
                    <button
                      className={`flex w-full items-start justify-between gap-2 px-4 py-3 text-left transition hover:bg-slate-50 ${
                        selected === conversation.conversation_id
                          ? "bg-brand-50"
                          : ""
                      }`}
                      onClick={() =>
                        openConversation(conversation.conversation_id)
                      }
                    >
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-slate-800">
                          {conversation.title || "Untitled conversation"}
                        </p>
                        <p className="text-xs text-slate-400">
                          {conversation.message_count} messages
                        </p>
                      </div>
                      <span
                        className="shrink-0 text-xs text-red-500 hover:underline"
                        onClick={(event) => {
                          event.stopPropagation();
                          deleteConversation(conversation.conversation_id);
                        }}
                      >
                        delete
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card p-5">
            {!selected ? (
              <EmptyState
                icon="💬"
                title="Select a conversation"
                description="Choose a conversation from the list to read the full exchange."
              />
            ) : loadingMessages ? (
              <div className="flex justify-center py-16 text-brand-600">
                <Spinner className="h-6 w-6" />
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.message_id}
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
                      <p
                        className={`mt-2 text-[10px] ${
                          message.role === "user"
                            ? "text-brand-100"
                            : "text-slate-400"
                        }`}
                      >
                        {formatDateTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
