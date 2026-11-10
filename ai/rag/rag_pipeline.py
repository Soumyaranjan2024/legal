"""Retrieval-Augmented Generation pipeline for Indian legal information.

Flow: question -> embedding -> ChromaDB retrieval -> context -> LLM -> answer
with source references. When the knowledge base has nothing relevant, a web
search fallback answers from web results instead. The LLM is Grok (xAI), Groq
or Gemini; BGE/E5 provides embeddings; ChromaDB provides storage and semantic
retrieval.
"""

from typing import Optional

from ai.config.settings import settings
from ai.llm.provider import LLMClient, get_llm_client
from ai.rag.prompts.legal_prompts import (
    LEGAL_SYSTEM_PROMPT,
    WEB_SYSTEM_PROMPT,
    build_answer_prompt,
    build_web_answer_prompt,
)
from ai.rag.retrieval.retriever import LegalRetriever
from ai.rag.web_search import web_search
from ai.security.guardrails import (
    sanitize_document_text,
    sanitize_question,
)

NO_CONTEXT_ANSWER = (
    "No relevant legal information was found in the knowledge base for this "
    "question. Please try rephrasing, or upload the relevant Act or judgment "
    "document. This system provides legal information, not legal advice."
)

# Phrases the knowledge-base prompt tells the LLM to use when the retrieved
# documents do not actually contain the answer. When the "Direct Answer"
# section is such a placeholder, the knowledge base could not answer, so the
# web fallback kicks in. Later sections may legitimately be placeholders even
# for a good answer, so only the Direct Answer section is inspected.
_UNINFORMATIVE_MARKERS = (
    "not specified in the retrieved documents",
    "not available in the retrieved documents",
    "not mentioned in the retrieved documents",
    "not provided in the retrieved documents",
    "no relevant legal information was found",
)


class LegalRAGPipeline:
    """End-to-end RAG pipeline backed by the configured LLM and ChromaDB."""

    def __init__(
        self,
        top_k: int = None,
        retriever: Optional[LegalRetriever] = None,
        llm: Optional[LLMClient] = None,
    ):

        self.top_k = top_k or settings.TOP_K
        self._retriever = retriever
        self._llm = llm

    # --- Lazily constructed heavy dependencies --------------------------

    @property
    def retriever(self) -> LegalRetriever:

        if self._retriever is None:
            self._retriever = LegalRetriever(top_k=self.top_k)

        return self._retriever

    @property
    def llm(self) -> LLMClient:

        if self._llm is None:
            self._llm = get_llm_client()

        return self._llm

    # --- Retrieval ------------------------------------------------------

    def retrieve_documents(
        self,
        question: str,
        top_k: int = None,
        where: dict = None,
    ) -> list:

        return self.retriever.retrieve(
            question,
            top_k=top_k or self.top_k,
            where=where,
        )

    # --- Web-search fallback --------------------------------------------

    def _needs_web_search(self, documents: list) -> bool:
        """True when the knowledge base is *clearly* irrelevant.

        This is only a fast path for obviously off-topic questions; the
        tighter gray zone is caught later by ``_is_uninformative`` after the
        knowledge-base answer is generated.
        """

        if not settings.WEB_SEARCH_ENABLED:
            return False

        if not documents:
            return True

        distances = [
            document.get("distance")
            for document in documents
            if document.get("distance") is not None
        ]

        if not distances:
            return False

        return min(distances) > settings.WEB_SEARCH_MAX_DISTANCE

    @staticmethod
    def _is_uninformative(answer: str) -> bool:
        """True when a knowledge-base answer did not actually answer.

        Only the ``Direct Answer`` section is inspected: if that is a
        placeholder the knowledge base had nothing, even if later sections
        happen to be filled in.
        """

        if not answer or not answer.strip():
            return True

        lowered = answer.lower()
        marker = "direct answer"

        start = lowered.find(marker)
        if start == -1:
            return any(m in lowered for m in _UNINFORMATIVE_MARKERS)

        section = lowered[start + len(marker):]
        next_heading = section.find("##")
        if next_heading != -1:
            section = section[:next_heading]

        return any(m in section for m in _UNINFORMATIVE_MARKERS)

    @staticmethod
    def _document_sources(documents: list) -> list:
        """Map retrieved knowledge-base documents to source records."""

        return [
            {
                "document": document["source"],
                "document_id": document.get("document_id"),
                "page": document.get("page"),
                "chunk_index": document.get("chunk_index"),
                "court_type": document.get("court_type"),
                "court_name": document.get("court_name"),
                "distance": document.get("distance"),
            }
            for document in documents
        ]

    def _generate_web_answer(self, question: str) -> Optional[dict]:
        """Answer from web search results, or None if unavailable."""

        results = web_search(question)

        if not results:
            return None

        prompt = build_web_answer_prompt(question, results)

        try:
            answer = self.llm.generate_response(
                prompt,
                system_prompt=WEB_SYSTEM_PROMPT,
            )
        except Exception:
            return None

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "document": result.get("title") or result.get("url"),
                    "document_id": None,
                    "page": None,
                    "chunk_index": None,
                    "court_type": None,
                    "court_name": None,
                    "distance": None,
                    "source_url": result.get("url"),
                }
                for result in results
            ],
            "retrieved_count": len(results),
        }

    # --- Answer generation ----------------------------------------------

    def generate_answer(
        self,
        question: str,
        top_k: int = None,
        where: dict = None,
    ) -> dict:

        question = sanitize_question(question)

        documents = self.retrieve_documents(
            question,
            top_k=top_k,
            where=where,
        )

        # Neutralise any injected instructions inside retrieved text.
        for document in documents:
            document["text"] = sanitize_document_text(
                document.get("text", "")
            )

        # Answer from the knowledge base first when it has something relevant.
        kb_answer = None
        if documents and not self._needs_web_search(documents):
            prompt = build_answer_prompt(question, documents)
            kb_answer = self.llm.generate_response(
                prompt,
                system_prompt=LEGAL_SYSTEM_PROMPT,
            )

            # The knowledge base answered properly -> use it.
            if not self._is_uninformative(kb_answer):
                return {
                    "question": question,
                    "answer": kb_answer,
                    "sources": self._document_sources(documents),
                    "retrieved_count": len(documents),
                }

        # Knowledge base had nothing relevant (or could not answer) -> web.
        web_result = self._generate_web_answer(question)

        if web_result is not None:
            return web_result

        # Web fallback unavailable: return the best knowledge-base result.
        if kb_answer is not None:
            return {
                "question": question,
                "answer": kb_answer,
                "sources": self._document_sources(documents),
                "retrieved_count": len(documents),
            }

        return {
            "question": question,
            "answer": NO_CONTEXT_ANSWER,
            "sources": [],
            "retrieved_count": 0,
        }
