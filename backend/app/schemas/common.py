"""Pydantic schemas shared across the API."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A simple human-readable message."""

    detail: str


class Pagination(BaseModel):
    total: int = 0
    limit: int = 50
    offset: int = 0


class LegalSource(BaseModel):
    """A source reference returned alongside a generated answer."""

    document: str = "Unknown"
    document_id: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    court_type: Optional[str] = None
    court_name: Optional[str] = None
    distance: Optional[float] = None
    source_url: Optional[str] = None


class DisclaimerMixin(BaseModel):
    """Adds the standard legal-information disclaimer to a response."""

    disclaimer: str = Field(
        default=(
            "This platform provides legal information, not professional "
            "legal advice. Please consult a qualified lawyer for advice on "
            "your specific situation."
        )
    )


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_configured: bool
    llm_provider: str = ""
    chroma: dict
    collections: List[dict] = []
    extra: Optional[dict[str, Any]] = None
