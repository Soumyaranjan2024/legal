from pathlib import Path


def extract_document_metadata(
    document: dict,
    entities: dict | None = None
) -> dict:
    """
    Extract structured metadata from a preprocessed legal document.
    """

    if not isinstance(document, dict):
        raise TypeError("Document must be a dictionary.")

    required_fields = [
        "file_name",
        "page_count",
        "metadata",
        "ocr_used",
        "full_text"
    ]

    for field in required_fields:
        if field not in document:
            raise ValueError(
                f"Missing required document field: {field}"
            )

    if not isinstance(document["metadata"], dict):
        raise TypeError("PDF metadata must be a dictionary.")

    if entities is None:
        entities = {}

    if not isinstance(entities, dict):
        raise TypeError("Entities must be a dictionary.")

    file_name = document["file_name"]
    pdf_metadata = document["metadata"]

    metadata = {
        "document_id": Path(file_name).stem,
        "file_name": file_name,
        "file_extension": Path(file_name).suffix.lower(),
        "page_count": document["page_count"],

        "document_metadata": {
            "title": pdf_metadata.get("title"),
            "author": pdf_metadata.get("author"),
            "subject": pdf_metadata.get("subject"),
            "creator": pdf_metadata.get("creator"),
            "producer": pdf_metadata.get("producer"),
            "creation_date": pdf_metadata.get("creationDate"),
            "modification_date": pdf_metadata.get("modDate")
        },

        "processing_metadata": {
            "ocr_used": document["ocr_used"],
            "source_type": (
                "scanned_or_ocr_processed"
                if document["ocr_used"]
                else "text_based_pdf"
            ),
            "extracted_character_count": len(
                document["full_text"]
            )
        },

        "legal_metadata": {
            "acts": entities.get("acts", []),
            "sections": entities.get("sections", []),
            "dates": entities.get("dates", []),
            "courts": entities.get("courts", []),
            "case_references": entities.get(
                "case_references", []
            )
        }
    }

    return metadata