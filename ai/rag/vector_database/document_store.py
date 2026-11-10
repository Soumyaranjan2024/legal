"""ChromaDB-backed storage for legal document records.

Stores document-level details, source metadata and the serialized structured
JSON produced by Grok. ChromaDB metadata only supports scalar values, so
nested/list fields are serialized into the JSON document body.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from ai.config.settings import settings
from ai.rag.vector_database.chroma_client import get_or_create_collection

# Placeholder embedding so document records do not trigger ChromaDB's default
# embedding function (semantic search is served by the legal_chunks collection).
_PLACEHOLDER_EMBEDDING = [0.0]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LegalDocumentStore:
    """Store and manage legal document records in ChromaDB."""

    def __init__(self, collection_name: str = None):

        self.collection_name = (
            collection_name or settings.LEGAL_DOCUMENTS_COLLECTION
        )

        self.collection = get_or_create_collection(self.collection_name)

    def upsert_document(
        self,
        document_id: str,
        payload: dict,
        metadata: dict,
    ) -> None:
        """Insert or update a document record."""

        clean_metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }

        clean_metadata["document_id"] = document_id
        clean_metadata.setdefault("ingested_at", _now())

        self.collection.upsert(
            ids=[document_id],
            documents=[json.dumps(payload, ensure_ascii=False)],
            embeddings=[_PLACEHOLDER_EMBEDDING],
            metadatas=[clean_metadata],
        )

    def exists(self, document_id: str) -> bool:
        result = self.collection.get(ids=[document_id])
        return bool(result.get("ids"))

    def get_document(self, document_id: str) -> Optional[dict]:
        """Return a single document record with its parsed JSON body."""

        result = self.collection.get(ids=[document_id])

        if not result.get("ids"):
            return None

        try:
            payload = json.loads(result["documents"][0])
        except (json.JSONDecodeError, TypeError):
            payload = {}

        return {
            "document_id": document_id,
            "metadata": result["metadatas"][0] or {},
            "document": payload,
        }

    def get_payload(self, document_id: str) -> Optional[dict]:
        record = self.get_document(document_id)
        return record["document"] if record else None

    def list_documents(self) -> list:
        """Return all document records (metadata + parsed JSON body)."""

        result = self.collection.get(include=["documents", "metadatas"])

        documents = []

        for index, document_id in enumerate(result.get("ids", [])):

            try:
                payload = json.loads(result["documents"][index])
            except (json.JSONDecodeError, TypeError):
                payload = {}

            documents.append({
                "document_id": document_id,
                "metadata": result["metadatas"][index] or {},
                "document": payload,
            })

        return documents

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(ids=[document_id])

    def count(self) -> int:
        return self.collection.count()
