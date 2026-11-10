"""Legal document and upload service."""

from pathlib import Path
from typing import Dict, List, Optional

from ai.config.settings import settings
from ai.rag.vector_database.document_store import LegalDocumentStore
from ai.rag.vector_database.vector_store import LegalVectorStore
from backend.app.core.logging_config import get_logger
from backend.app.schemas.document import DocumentDetail, DocumentSummary
from backend.app.services.ai_runtime import get_ingestion_pipeline

logger = get_logger(__name__)

_PDF_MAGIC = b"%PDF"


class DocumentService:
    """Manage ingestion, listing and removal of legal documents."""

    def __init__(
        self,
        document_store: Optional[LegalDocumentStore] = None,
        vector_store: Optional[LegalVectorStore] = None,
    ):

        self.document_store = document_store or LegalDocumentStore()
        self.vector_store = vector_store or LegalVectorStore()

    # --- Chunk accounting ----------------------------------------------

    def _chunk_counts(self) -> Dict[str, int]:
        """Return {document_id: chunk_count} using a single collection read."""

        counts: Dict[str, int] = {}

        result = self.vector_store.collection.get(include=["metadatas"])

        for metadata in result.get("metadatas", []) or []:
            document_id = (metadata or {}).get("document_id")
            if document_id:
                counts[document_id] = counts.get(document_id, 0) + 1

        return counts

    # --- Mapping --------------------------------------------------------

    @staticmethod
    def _summary(record: dict, chunk_count: int = 0) -> DocumentSummary:

        metadata = record.get("metadata", {}) or {}

        return DocumentSummary(
            document_id=record["document_id"],
            file_name=metadata.get("file_name", ""),
            title=metadata.get("title", ""),
            source_type=metadata.get("source_type", ""),
            source_url=metadata.get("source_url") or None,
            legal_category=metadata.get("legal_category", ""),
            court_type=metadata.get("court_type", ""),
            court_name=metadata.get("court_name", ""),
            case_name=metadata.get("case_name", ""),
            case_number=metadata.get("case_number", ""),
            judgment_date=metadata.get("judgment_date", ""),
            acts=metadata.get("acts", ""),
            sections=metadata.get("sections", ""),
            page_count=int(metadata.get("page_count", 0) or 0),
            ocr_used=bool(metadata.get("ocr_used", False)),
            content_hash=metadata.get("content_hash", ""),
            ingested_at=metadata.get("ingested_at"),
            chunk_count=chunk_count,
        )

    def list_documents(self) -> List[DocumentSummary]:

        counts = self._chunk_counts()

        return [
            self._summary(record, counts.get(record["document_id"], 0))
            for record in self.document_store.list_documents()
        ]

    def get_document(self, document_id: str) -> Optional[DocumentDetail]:

        record = self.document_store.get_document(document_id)

        if record is None:
            return None

        payload = record.get("document", {}) or {}
        summary = self._summary(record, self._chunk_counts().get(document_id, 0))

        return DocumentDetail(
            **summary.model_dump(),
            metadata=record.get("metadata", {}) or {},
            extracted_information=payload.get("extracted_information", {}) or {},
        )

    def find_by_hash(self, content_hash: str) -> Optional[str]:
        """Return an existing document_id for the same content hash."""

        for record in self.document_store.list_documents():
            if (record.get("metadata", {}) or {}).get("content_hash") == content_hash:
                return record["document_id"]

        return None

    # --- Mutations ------------------------------------------------------

    def delete_document(self, document_id: str) -> bool:

        if not self.document_store.exists(document_id):
            return False

        self.vector_store.delete_by_document(document_id)
        self.document_store.delete_document(document_id)

        return True

    @staticmethod
    def _validate_upload(filename: str, content: bytes) -> None:
        """Validate extension, size and PDF signature before ingestion."""

        extension = Path(filename).suffix.lower()

        if extension not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{extension or 'unknown'}'. "
                f"Allowed: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}."
            )

        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

        if len(content) > max_bytes:
            raise ValueError(
                f"File exceeds the {settings.MAX_UPLOAD_MB} MB limit."
            )

        if not content.startswith(_PDF_MAGIC):
            raise ValueError("The uploaded file is not a valid PDF document.")

    def ingest_upload(
        self,
        filename: str,
        content: bytes,
        source_url: Optional[str] = None,
        source_type: str = "manual_upload",
    ) -> dict:
        """Validate and run a manual PDF upload through the pipeline."""

        safe_name = Path(filename).name
        self._validate_upload(safe_name, content)

        upload_dir = Path(settings.UPLOAD_DIRECTORY)
        upload_dir.mkdir(parents=True, exist_ok=True)

        destination = upload_dir / safe_name
        destination.write_bytes(content)

        logger.info("Ingesting uploaded document: %s", safe_name)

        result = get_ingestion_pipeline().ingest_document(
            str(destination),
            source_url=source_url,
        )

        result["source_type"] = source_type

        return result

    def ingest_from_url(self, url: str, filename: Optional[str] = None) -> dict:
        """Download a PDF from a source URL and ingest it."""

        logger.info("Ingesting document from URL: %s", url)

        return get_ingestion_pipeline().ingest_from_url(url, filename=filename)

    # --- Stats ----------------------------------------------------------

    def count(self) -> int:
        return self.document_store.count()

    def chunk_total(self) -> int:
        return self.vector_store.count_documents()
