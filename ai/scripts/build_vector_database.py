"""Build the ChromaDB knowledge base from local PDF datasets.

Usage:
    python -m ai.scripts.build_vector_database
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ai.config.settings import settings
from ai.data_pipeline.ingestion_pipeline import LegalIngestionPipeline
from ai.rag.vector_database.vector_store import LegalVectorStore
from ai.rag.vector_database.document_store import LegalDocumentStore


def main():

    raw_directory = Path(settings.UPLOAD_DIRECTORY)

    pdf_files = sorted(raw_directory.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {raw_directory}")
        return

    print(f"Found {len(pdf_files)} PDF document(s) in {raw_directory}\n")

    pipeline = LegalIngestionPipeline()

    succeeded = 0
    failed = 0

    for pdf_path in pdf_files:

        print("=" * 70)
        print(f"Ingesting: {pdf_path.name}")
        print("=" * 70)

        try:
            result = pipeline.ingest_document(str(pdf_path))
            succeeded += 1

            print(
                f"  -> document_id: {result['document_id']}\n"
                f"  -> chunks: {result['total_chunks']}\n"
                f"  -> OCR used: {result['ocr_used']}"
            )

        except Exception as error:
            failed += 1
            print(f"  -> FAILED: {error}")

        print()

    vector_store = LegalVectorStore()
    document_store = LegalDocumentStore()

    print("=" * 70)
    print("VECTOR DATABASE SUMMARY")
    print("=" * 70)
    print(f"Documents ingested : {succeeded} (failed: {failed})")
    print(f"Document records   : {document_store.count()}")
    print(f"Chunks in ChromaDB : {vector_store.count_documents()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
