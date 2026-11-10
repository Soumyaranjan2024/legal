"""System health and public statistics routes."""

from fastapi import APIRouter

from ai.rag.vector_database.document_store import LegalDocumentStore
from ai.rag.vector_database.vector_store import LegalVectorStore
from backend.app.core.config import config
from backend.app.db.chroma import chroma_health, collection_stats
from backend.app.schemas.common import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness and dependency status."""

    return HealthResponse(
        status="ok",
        version=config.VERSION,
        llm_configured=config.llm_configured,
        llm_provider=config.llm_provider,
        chroma=chroma_health(),
        collections=collection_stats(),
        extra={
            "embedding_model": config.EMBEDDING_MODEL,
            "llm_model": config.llm_model,
        },
    )


@router.get("/system/status")
def status() -> dict:
    """Detailed component status for dashboards."""

    return {
        "api": {"status": "ok", "version": config.VERSION},
        "llm": {
            "configured": config.llm_configured,
            "provider": config.llm_provider,
            "model": config.llm_model,
        },
        "embeddings": {"model": config.EMBEDDING_MODEL},
        "chroma": chroma_health(),
        "collections": collection_stats(),
    }


@router.get("/system/stats")
def public_stats() -> dict:
    """Public knowledge-base statistics (no authentication required)."""

    documents = LegalDocumentStore()
    chunks = LegalVectorStore()

    return {
        "documents": documents.count(),
        "chunks": chunks.count_documents(),
        "sources": len(chunks.list_sources()),
        "llm_configured": config.llm_configured,
        "llm_provider": config.llm_provider,
        "embedding_model": config.EMBEDDING_MODEL,
    }
