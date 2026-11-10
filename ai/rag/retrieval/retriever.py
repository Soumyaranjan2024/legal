"""Semantic retriever over the legal_chunks ChromaDB collection."""

from ai.config.settings import settings
from ai.rag.embeddings.embedding_service import EmbeddingService
from ai.rag.vector_database.vector_store import LegalVectorStore

# Cover pages, tables of contents and Act preambles ("An Act to amend ...")
# match an Act's name strongly but carry no substantive law, so they are
# filtered out after an over-fetch.
_CANDIDATE_MULTIPLIER = 4
_MIN_USEFUL_CHARS = 90
_LOW_VALUE_MARKERS = (
    "arrangement of sections",
    "table of contents",
    "as on the",
    "an act to amend",
    "an act to consolidate",
    "an act to provide",
    "an act to regulate",
    "an act further to amend",
)


def _is_low_value(text: str) -> bool:
    """True for cover-page / table-of-contents style chunks."""

    if not text or not text.strip():
        return True

    compact = " ".join(text.split())
    lowered = compact.lower()

    if any(marker in lowered for marker in _LOW_VALUE_MARKERS):
        return True

    return len(compact) < _MIN_USEFUL_CHARS


class LegalRetriever:
    """Retrieve relevant legal chunks for a natural-language question."""

    def __init__(
        self,
        top_k: int = None,
        embedding_service: EmbeddingService = None,
        vector_store: LegalVectorStore = None,
    ):

        self.top_k = top_k or settings.TOP_K
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )
        self.vector_store = (
            vector_store or LegalVectorStore()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        where: dict = None,
    ) -> list:
        """Return the top-k chunks most similar to the query."""

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        top_k = top_k or self.top_k

        query_embedding = self.embedding_service.encode_query(query)

        # Over-fetch so cover/TOC chunks can be dropped without losing reach.
        candidate_k = max(top_k * _CANDIDATE_MULTIPLIER, top_k + 5)

        results = self.vector_store.search(
            query_embedding,
            top_k=candidate_k,
            where=where,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        chunks = []

        for index, text in enumerate(documents):

            metadata = (
                metadatas[index] if index < len(metadatas) else {}
            ) or {}

            chunks.append({
                "text": text,
                "source": metadata.get("source", "Unknown"),
                "document_id": metadata.get("document_id"),
                "page": metadata.get("page_number"),
                "chunk_index": metadata.get("chunk_index"),
                "court_type": metadata.get("court_type"),
                "court_name": metadata.get("court_name"),
                "acts": metadata.get("acts"),
                "sections": metadata.get("sections"),
                "distance": (
                    distances[index]
                    if index < len(distances)
                    else None
                ),
                "metadata": metadata,
            })

        filtered = [chunk for chunk in chunks if not _is_low_value(chunk["text"])]

        # Never return fewer than requested if filtering removed too much.
        return (filtered or chunks)[:top_k]

    def count(self) -> int:
        return self.vector_store.count_documents()
