"""ChromaDB access helpers for the backend.

ChromaDB is the only database. This module exposes the collections used by the
API: legal documents, legal chunks, users and chat history.
"""

from typing import List

from ai.config.settings import settings
from ai.rag.vector_database.chroma_client import (
    get_chroma_client,
    get_or_create_collection,
)


def users_collection():
    return get_or_create_collection(settings.USERS_COLLECTION)


def chat_history_collection():
    return get_or_create_collection(settings.CHAT_HISTORY_COLLECTION)


def documents_collection():
    return get_or_create_collection(settings.LEGAL_DOCUMENTS_COLLECTION)


def chunks_collection():
    return get_or_create_collection(settings.LEGAL_CHUNKS_COLLECTION)


def collection_stats() -> List[dict]:
    """Return name and record count for every collection."""

    client = get_chroma_client()

    stats = []

    for collection in client.list_collections():
        stats.append({
            "name": collection.name,
            "count": collection.count(),
        })

    return stats


def chroma_health() -> dict:
    """Return basic ChromaDB health information."""

    try:
        client = get_chroma_client()
        names = [collection.name for collection in client.list_collections()]

        return {
            "status": "connected",
            "persist_directory": settings.CHROMA_PERSIST_DIRECTORY,
            "collections": names,
        }

    except Exception as error:  # pragma: no cover - defensive
        return {
            "status": "error",
            "detail": str(error),
        }
