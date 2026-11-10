"""Shared ChromaDB client.

ChromaDB is the ONLY database used by this system and uses persistent local
storage. This module provides a single persistent client and helper for
creating / opening collections so the same storage is reused everywhere.
"""

from pathlib import Path

import chromadb

from ai.config.settings import settings

_client = None


def get_chroma_client() -> "chromadb.ClientAPI":
    """Return a singleton persistent ChromaDB client."""

    global _client

    if _client is None:

        Path(settings.CHROMA_PERSIST_DIRECTORY).mkdir(
            parents=True,
            exist_ok=True,
        )

        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )

    return _client


def get_or_create_collection(
    name: str,
    metadata: dict = None,
) -> "chromadb.Collection":
    """Open (or create) a collection by name."""

    if metadata is None:
        metadata = {"hnsw:space": "cosine"}

    return get_chroma_client().get_or_create_collection(
        name=name,
        metadata=metadata,
    )


def reset_client() -> None:
    """Drop the cached client (used in tests)."""

    global _client
    _client = None
