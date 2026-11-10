"""Document & upload schemas."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):

    document_id: str
    file_name: str = ""
    title: str = ""
    source_type: str = ""
    source_url: Optional[str] = None
    legal_category: str = ""
    court_type: str = ""
    court_name: str = ""
    case_name: str = ""
    case_number: str = ""
    judgment_date: str = ""
    acts: str = ""
    sections: str = ""
    page_count: int = 0
    ocr_used: bool = False
    content_hash: str = ""
    ingested_at: Optional[str] = None
    chunk_count: int = 0


class DocumentDetail(DocumentSummary):

    metadata: dict[str, Any] = {}
    extracted_information: dict[str, Any] = {}


class DocumentListResponse(BaseModel):

    total: int
    documents: List[DocumentSummary]


class UploadSourceOption(BaseModel):

    value: str
    label: str


class UploadRequest(BaseModel):
    """Metadata supplied with a manual PDF upload (multipart form fields)."""

    title: Optional[str] = None
    source_url: Optional[str] = Field(default=None, max_length=1000)
    source_type: str = "manual_upload"


class UploadResponse(BaseModel):

    document_id: str
    file_name: str
    page_count: int
    total_chunks: int
    ocr_used: bool
    is_valid: bool
    detail: str


class IngestUrlRequest(BaseModel):

    url: str = Field(min_length=8, max_length=1000)
    filename: Optional[str] = None


class DeleteResponse(BaseModel):

    detail: str
    document_id: str
