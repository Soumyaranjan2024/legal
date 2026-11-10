"""Search schemas (keyword + semantic)."""

from typing import List, Optional

from pydantic import BaseModel, Field

from backend.app.schemas.common import LegalSource


class SearchRequest(BaseModel):

    query: str = Field(min_length=2, max_length=500)
    mode: str = Field(default="semantic", pattern="^(semantic|keyword|hybrid)$")
    top_k: int = Field(default=5, ge=1, le=20)
    court_type: Optional[str] = None
    acts: Optional[str] = None


class SearchResult(BaseModel):

    text: str
    source: str = "Unknown"
    document_id: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    court_type: Optional[str] = None
    court_name: Optional[str] = None
    acts: Optional[str] = None
    sections: Optional[str] = None
    score: Optional[float] = None
    title: Optional[str] = None
    source_url: Optional[str] = None


class SearchResponse(BaseModel):

    query: str
    mode: str
    total: int
    results: List[SearchResult]
    sources: List[LegalSource] = []


class SearchFilterOptions(BaseModel):

    court_types: List[str] = []
    acts: List[str] = []
    categories: List[str] = []
