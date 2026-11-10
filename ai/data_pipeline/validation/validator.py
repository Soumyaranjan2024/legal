import json


def validate_document_data(data: dict) -> dict:
    """Validate extracted legal document metadata."""

    errors = []

    if not isinstance(data, dict):
        return {
            "is_valid": False,
            "errors": ["Input must be a dictionary."]
        }

    required_fields = [
        "document_id",
        "file_name",
        "file_extension",
        "page_count",
        "document_metadata",
        "processing_metadata",
        "legal_metadata"
    ]

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return {"is_valid": False, "errors": errors}

    if not isinstance(data["document_id"], str) or not data["document_id"].strip():
        errors.append("document_id must be a non-empty string.")

    if not isinstance(data["file_name"], str) or not data["file_name"].strip():
        errors.append("file_name must be a non-empty string.")

    if data["file_extension"] != ".pdf":
        errors.append("file_extension must be '.pdf'.")

    if (
        not isinstance(data["page_count"], int)
        or isinstance(data["page_count"], bool)
        or data["page_count"] <= 0
    ):
        errors.append("page_count must be a positive integer.")

    document_metadata = data["document_metadata"]

    if not isinstance(document_metadata, dict):
        errors.append("document_metadata must be a dictionary.")
    else:
        expected_fields = [
            "title", "author", "subject", "creator",
            "producer", "creation_date", "modification_date"
        ]

        for field in expected_fields:
            if field not in document_metadata:
                errors.append(f"Missing document metadata field: {field}")
            elif document_metadata[field] is not None and not isinstance(
                document_metadata[field], str
            ):
                errors.append(f"{field} must be a string or None.")

    processing_metadata = data["processing_metadata"]

    if not isinstance(processing_metadata, dict):
        errors.append("processing_metadata must be a dictionary.")
    else:
        if not isinstance(processing_metadata.get("ocr_used"), bool):
            errors.append("ocr_used must be a boolean.")

        if not isinstance(processing_metadata.get("source_type"), str):
            errors.append("source_type must be a string.")

        count = processing_metadata.get("extracted_character_count")

        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            errors.append("extracted_character_count must be non-negative.")

    legal_metadata = data["legal_metadata"]

    if not isinstance(legal_metadata, dict):
        errors.append("legal_metadata must be a dictionary.")
    else:
        expected_fields = [
            "acts", "sections", "dates", "courts", "case_references"
        ]

        for field in expected_fields:
            if field not in legal_metadata:
                errors.append(f"Missing legal metadata field: {field}")
            elif not isinstance(legal_metadata[field], list):
                errors.append(f"{field} must be a list.")
            elif not all(
                isinstance(item, str) for item in legal_metadata[field]
            ):
                errors.append(f"All items in {field} must be strings.")

    try:
        json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        errors.append("Data cannot be serialized into JSON.")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }