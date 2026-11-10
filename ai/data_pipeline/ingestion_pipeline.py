"""Complete legal document ingestion pipeline.

PDF -> Preprocessing (extract + OCR + clean) -> Regex entities
-> Grok structured extraction -> Metadata -> JSON -> Pydantic validation
-> Chunking -> Embeddings -> ChromaDB (chunks + document record).
"""

import hashlib
from pathlib import Path
from typing import Optional

from ai.config.settings import settings

from ai.data_pipeline.preprocessing.document_preprocessor import (
    preprocess_document,
)
from ai.data_pipeline.preprocessing.chunking import chunk_legal_document
from ai.data_pipeline.information_extraction.entity_extractor import (
    extract_legal_entities,
)
from ai.data_pipeline.information_extraction.metadata_extractor import (
    extract_document_metadata,
)
from ai.data_pipeline.information_extraction.grok_extractor import (
    safe_extract_legal_information,
)
from ai.data_pipeline.json_converter.json_converter import convert_to_json
from ai.data_pipeline.validation.validator import validate_document_data
from ai.data_pipeline.download.document_downloader import download_pdf

from ai.rag.embeddings.embedding_service import EmbeddingService
from ai.rag.vector_database.vector_store import LegalVectorStore
from ai.rag.vector_database.document_store import LegalDocumentStore


def _file_hash(path: Path) -> str:
    """Compute a SHA-256 content hash for duplicate detection."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def _scalar_metadata(metadata: dict) -> dict:
    """Keep only ChromaDB-supported scalar metadata values."""

    return {
        key: value
        for key, value in metadata.items()
        if value is not None and isinstance(value, (str, int, float, bool))
    }


class LegalIngestionPipeline:
    """Complete legal document ingestion pipeline."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[LegalVectorStore] = None,
        document_store: Optional[LegalDocumentStore] = None,
    ):

        self.embedding_service = (
            embedding_service or EmbeddingService()
        )
        self.vector_store = vector_store or LegalVectorStore()
        self.document_store = document_store or LegalDocumentStore()

    def ingest_document(
        self,
        pdf_path: str,
        source_url: Optional[str] = None,
    ) -> dict:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF document not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF documents are supported.")

        content_hash = _file_hash(pdf_path)

        # STEP 1: Document preprocessing (extract + OCR + clean).
        document = preprocess_document(str(pdf_path))

        # STEP 2: Regex-based legal entity extraction.
        entities = extract_legal_entities(document["full_text"])

        # STEP 3: Grok structured legal information extraction.
        extracted = safe_extract_legal_information(document["full_text"])

        # STEP 4: Metadata assembly (regex + Grok enrichment).
        metadata = extract_document_metadata(document, entities)

        metadata["processing_metadata"]["content_hash"] = content_hash
        metadata["processing_metadata"]["source_url"] = source_url
        metadata["extracted_information"] = extracted

        # Enrich regex legal metadata with Grok findings when missing.
        legal_metadata = metadata["legal_metadata"]

        if not legal_metadata["acts"] and extracted["applicable_acts"]:
            legal_metadata["acts"] = extracted["applicable_acts"]

        if not legal_metadata["sections"] and extracted["applicable_sections"]:
            legal_metadata["sections"] = extracted["applicable_sections"]

        if not legal_metadata["courts"] and extracted["court_name"]:
            legal_metadata["courts"] = [extracted["court_name"]]

        if not legal_metadata["case_references"] and extracted["source_references"]:
            legal_metadata["case_references"] = extracted["source_references"]

        document_id = metadata["document_id"]

        # STEP 5: JSON conversion.
        metadata_directory = Path("datasets/processed/metadata")
        metadata_directory.mkdir(parents=True, exist_ok=True)

        json_path = metadata_directory / f"{pdf_path.stem}.json"
        convert_to_json(metadata, str(json_path))

        # STEP 6: Pydantic + rule validation.
        validation = validate_document_data(metadata)

        if not validation["is_valid"]:
            raise ValueError(
                "Document validation failed: "
                + str(validation["errors"])
            )

        # STEP 7: Chunking with enriched legal metadata.
        chunks = chunk_legal_document(document)

        if not chunks:
            raise ValueError("No text chunks were generated.")

        chunk_metadata = _scalar_metadata({
            "document_id": document_id,
            "court_type": extracted.get("court_type"),
            "court_name": extracted.get("court_name"),
            "legal_category": extracted.get("legal_category"),
            "acts": "; ".join(legal_metadata["acts"]),
            "sections": "; ".join(legal_metadata["sections"]),
            "source_url": source_url,
        })

        for chunk in chunks:
            chunk["metadata"].update(chunk_metadata)

        # STEP 8: Embedding generation.
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.encode_documents(texts)

        # STEP 9: ChromaDB storage (duplicate-safe).
        self.vector_store.delete_by_document(document_id)
        stored_count = self.vector_store.add_documents(chunks, embeddings)

        # STEP 10: Store the document-level record.
        self.document_store.upsert_document(
            document_id,
            payload=metadata,
            metadata=_scalar_metadata({
                "file_name": metadata["file_name"],
                "title": extracted.get("case_name")
                or metadata["document_metadata"].get("title"),
                "source_type": metadata["processing_metadata"]["source_type"],
                "ocr_used": metadata["processing_metadata"]["ocr_used"],
                "page_count": metadata["page_count"],
                "content_hash": content_hash,
                "source_url": source_url or "",
                "legal_category": extracted.get("legal_category") or "",
                "court_type": extracted.get("court_type") or "",
                "court_name": extracted.get("court_name") or "",
                "case_name": extracted.get("case_name") or "",
                "case_number": extracted.get("case_number") or "",
                "judgment_date": extracted.get("judgment_date") or "",
                "acts": "; ".join(legal_metadata["acts"]),
                "sections": "; ".join(legal_metadata["sections"]),
            }),
        )

        return {
            "document_id": document_id,
            "file_name": metadata["file_name"],
            "page_count": metadata["page_count"],
            "ocr_used": metadata["processing_metadata"]["ocr_used"],
            "content_hash": content_hash,
            "entities": entities,
            "extracted_information": extracted,
            "metadata_file": str(json_path),
            "total_chunks": len(chunks),
            "embeddings_generated": len(embeddings),
            "chunks_stored": stored_count,
            "database_total_chunks": self.vector_store.count_documents(),
            "is_valid": validation["is_valid"],
        }

    def ingest_from_url(
        self,
        url: str,
        filename: str = None,
    ) -> dict:

        downloaded_path = download_pdf(
            url=url,
            output_dir=settings.UPLOAD_DIRECTORY,
            filename=filename,
        )

        return self.ingest_document(downloaded_path, source_url=url)
