"""ChromaDB-backed storage for legal text chunks and their embeddings."""

from ai.config.settings import settings
from ai.rag.vector_database.chroma_client import get_or_create_collection


def _empty_result() -> dict:
    return {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }


class LegalVectorStore:
    """Store and retrieve legal document chunk embeddings in ChromaDB."""

    def __init__(self, collection_name: str = None):

        self.collection_name = (
            collection_name or settings.LEGAL_CHUNKS_COLLECTION
        )

        self.collection = get_or_create_collection(
            self.collection_name
        )

    def add_documents(self, chunks: list, embeddings: list) -> int:
        """Insert or update chunks together with their embeddings."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        if not chunks:
            return 0

        self.collection.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks],
        )

        return len(chunks)

    def search(
        self,
        query_embedding: list,
        top_k: int = 5,
        where: dict = None,
    ) -> dict:
        """Semantic search over stored chunks with optional metadata filter."""

        if not query_embedding:
            raise ValueError("Query embedding cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        total = self.collection.count()

        if total == 0:
            return _empty_result()

        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, total),
            "include": ["documents", "metadatas", "distances"],
        }

        if where:
            query_kwargs["where"] = where

        return self.collection.query(**query_kwargs)

    def delete_by_document(self, document_id: str) -> None:
        """Remove all chunks that belong to a document."""

        self.collection.delete(where={"document_id": document_id})

    def get_adjacent_chunks(
        self,
        source: str,
        page_number: int,
        chunk_index: int,
        window: int = 1,
    ) -> list:
        """Retrieve neighbouring chunks to recover split provisions."""

        if window < 0:
            raise ValueError("Window cannot be negative.")

        all_chunks = self.collection.get(
            where={"source": source},
            include=["documents", "metadatas"],
        )

        selected_chunks = []
        target_page = int(page_number)
        target_index = int(chunk_index)

        for index, metadata in enumerate(all_chunks["metadatas"]):

            current_page = int(metadata.get("page_number", -1))
            current_index = int(metadata.get("chunk_index", -1))

            if (
                abs(current_page - target_page) <= 1
                and (
                    current_page != target_page
                    or abs(current_index - target_index) <= window
                )
            ):

                selected_chunks.append({
                    "text": all_chunks["documents"][index],
                    "source": metadata.get("source", "Unknown"),
                    "page": current_page,
                    "chunk_index": current_index,
                })

        selected_chunks.sort(
            key=lambda item: (item["page"], item["chunk_index"])
        )

        return selected_chunks

    def count_documents(self) -> int:
        """Return the number of stored chunks."""

        return self.collection.count()

    def list_sources(self) -> list:
        """Return the distinct source file names stored in the collection."""

        result = self.collection.get(include=["metadatas"])

        sources = {
            metadata.get("source")
            for metadata in result.get("metadatas", [])
            if metadata.get("source")
        }

        return sorted(sources)
