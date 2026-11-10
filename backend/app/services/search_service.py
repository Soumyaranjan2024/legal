"""Search service: semantic (embeddings) and keyword (substring) retrieval."""

from typing import Dict, List, Optional

from ai.config.settings import settings
from ai.rag.vector_database.vector_store import LegalVectorStore
from backend.app.core.logging_config import get_logger
from backend.app.schemas.search import (
    SearchFilterOptions,
    SearchRequest,
    SearchResult,
)
from backend.app.services.ai_runtime import get_retriever

logger = get_logger(__name__)


def _build_where(court_type: Optional[str], acts: Optional[str]) -> Optional[dict]:
    clauses = []

    if court_type:
        clauses.append({"court_type": court_type})

    if not clauses:
        return None

    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


class SearchService:
    """Keyword and semantic search over the stored legal chunks."""

    def __init__(
        self,
        retriever=None,
        vector_store: Optional[LegalVectorStore] = None,
    ):

        self._retriever = retriever
        self.vector_store = vector_store or LegalVectorStore()

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = get_retriever()
        return self._retriever

    # --- Retrieval modes ------------------------------------------------

    def semantic(
        self,
        query: str,
        top_k: int,
        where: Optional[dict] = None,
    ) -> List[dict]:
        """Embedding-based similarity search."""

        chunks = self.retriever.retrieve(query, top_k=top_k, where=where)

        results = []

        for chunk in chunks:

            distance = chunk.get("distance")
            score = None if distance is None else round(1.0 - distance, 4)

            results.append({
                "text": chunk.get("text", ""),
                "source": chunk.get("source", "Unknown"),
                "document_id": chunk.get("document_id"),
                "page": chunk.get("page"),
                "chunk_index": chunk.get("chunk_index"),
                "court_type": chunk.get("court_type"),
                "court_name": chunk.get("court_name"),
                "acts": chunk.get("acts"),
                "sections": chunk.get("sections"),
                "score": score,
            })

        return results

    def keyword(
        self,
        query: str,
        top_k: int,
        where: Optional[dict] = None,
    ) -> List[dict]:
        """Substring search over chunk text using ChromaDB where_document."""

        get_kwargs = {
            "where_document": {"$contains": query},
            "include": ["documents", "metadatas"],
        }

        if where:
            get_kwargs["where"] = where

        result = self.vector_store.collection.get(**get_kwargs)

        documents = result.get("documents", []) or []
        metadatas = result.get("metadatas", []) or []

        results = []

        for index, text in enumerate(documents[:top_k]):

            metadata = metadatas[index] if index < len(metadatas) else {}

            results.append({
                "text": text,
                "source": metadata.get("source", "Unknown"),
                "document_id": metadata.get("document_id"),
                "page": metadata.get("page_number"),
                "chunk_index": metadata.get("chunk_index"),
                "court_type": metadata.get("court_type"),
                "court_name": metadata.get("court_name"),
                "acts": metadata.get("acts"),
                "sections": metadata.get("sections"),
                "score": None,
            })

        return results

    # --- Unified search -------------------------------------------------

    def search(self, request: SearchRequest) -> dict:
        """Run the requested search mode and normalise the output."""

        where = _build_where(request.court_type, request.acts)

        if request.mode == "keyword":

            raw = self.keyword(request.query, request.top_k, where)

        elif request.mode == "hybrid":

            raw = self._hybrid(request.query, request.top_k, where)

        else:

            raw = self.semantic(request.query, request.top_k, where)

        return {
            "query": request.query,
            "mode": request.mode,
            "total": len(raw),
            "results": raw,
        }

    def _hybrid(
        self,
        query: str,
        top_k: int,
        where: Optional[dict],
    ) -> List[dict]:
        """Merge semantic and keyword hits, de-duplicating chunks."""

        combined = self.semantic(query, top_k, where)
        combined += self.keyword(query, top_k, where)

        seen = set()
        merged = []

        for item in combined:

            key = (
                item.get("document_id"),
                item.get("page"),
                item.get("chunk_index"),
            )

            if key in seen:
                continue

            seen.add(key)
            merged.append(item)

        return merged[:top_k]

    # --- Filter options -------------------------------------------------

    def filter_options(self) -> SearchFilterOptions:
        """Distinct court types and acts available for filtering."""

        result = self.vector_store.collection.get(include=["metadatas"])

        court_types = set()
        acts = set()
        categories = set()

        for metadata in result.get("metadatas", []) or []:

            if not metadata:
                continue

            if metadata.get("court_type"):
                court_types.add(metadata["court_type"])

            if metadata.get("legal_category"):
                categories.add(metadata["legal_category"])

            if metadata.get("acts"):
                for act in str(metadata["acts"]).split(";"):
                    act = act.strip()
                    if act:
                        acts.add(act)

        return SearchFilterOptions(
            court_types=sorted(court_types),
            acts=sorted(acts),
            categories=sorted(categories),
        )

    def to_results(self, raw: List[dict]) -> List[SearchResult]:
        return [SearchResult(**item) for item in raw]
