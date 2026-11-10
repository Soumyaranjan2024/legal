"""Document and upload routes."""

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from backend.app.api.deps import get_current_user
from backend.app.core.logging_config import get_logger
from backend.app.schemas.document import (
    DeleteResponse,
    DocumentDetail,
    DocumentListResponse,
    IngestUrlRequest,
    UploadResponse,
)
from backend.app.schemas.user import UserPublic
from backend.app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = get_logger(__name__)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    user: UserPublic = Depends(get_current_user),
) -> DocumentListResponse:
    """List every ingested legal document."""

    documents = DocumentService().list_documents()

    return DocumentListResponse(total=len(documents), documents=documents)


@router.get("/stats")
def document_stats(user: UserPublic = Depends(get_current_user)) -> dict:
    """Return document and chunk counts."""

    service = DocumentService()

    return {
        "documents": service.count(),
        "chunks": service.chunk_total(),
    }


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    source_url: Optional[str] = Form(default=None),
    title: Optional[str] = Form(default=None),
    source_type: str = Form(default="manual_upload"),
    user: UserPublic = Depends(get_current_user),
) -> UploadResponse:
    """Upload a PDF, run the full ingestion pipeline and store it."""

    content = await file.read()

    service = DocumentService()

    try:
        result = service.ingest_upload(
            filename=file.filename or "upload.pdf",
            content=content,
            source_url=source_url,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    except Exception as error:
        logger.exception("Upload ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {error}",
        )

    return UploadResponse(
        document_id=result["document_id"],
        file_name=result["file_name"],
        page_count=result["page_count"],
        total_chunks=result["total_chunks"],
        ocr_used=result["ocr_used"],
        is_valid=result["is_valid"],
        detail="Document ingested successfully.",
    )


@router.post("/ingest-url", response_model=UploadResponse, status_code=201)
def ingest_url(
    payload: IngestUrlRequest,
    user: UserPublic = Depends(get_current_user),
) -> UploadResponse:
    """Download a PDF from an official source URL and ingest it."""

    service = DocumentService()

    try:
        result = service.ingest_from_url(payload.url, payload.filename)
    except Exception as error:
        logger.exception("URL ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not ingest from URL: {error}",
        )

    return UploadResponse(
        document_id=result["document_id"],
        file_name=result["file_name"],
        page_count=result["page_count"],
        total_chunks=result["total_chunks"],
        ocr_used=result["ocr_used"],
        is_valid=result["is_valid"],
        detail="Document downloaded and ingested successfully.",
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: str,
    user: UserPublic = Depends(get_current_user),
) -> DocumentDetail:
    """Return a single document with its structured extraction."""

    document = DocumentService().get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(
    document_id: str,
    user: UserPublic = Depends(get_current_user),
) -> DeleteResponse:
    """Delete a document and all of its chunks from ChromaDB."""

    if not DocumentService().delete_document(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return DeleteResponse(
        detail="Document deleted.",
        document_id=document_id,
    )
