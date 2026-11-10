"""Pydantic schemas for Grok-extracted legal information.

All extracted data is validated here. Missing information is represented as
``None`` or an empty list - never invented.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

_LIST_FIELDS = [
    "applicable_acts",
    "applicable_sections",
    "required_documents",
    "government_forms",
    "important_findings",
    "source_references",
]

_STR_FIELDS = [
    "case_name",
    "case_number",
    "legal_category",
    "court_type",
    "court_name",
    "legal_procedure",
    "timeline",
    "judgment_date",
]


class LegalExtraction(BaseModel):
    """Structured legal information extracted from a document by Grok."""

    case_name: Optional[str] = None
    case_number: Optional[str] = None
    legal_category: Optional[str] = None
    applicable_acts: List[str] = Field(default_factory=list)
    applicable_sections: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    court_type: Optional[str] = None
    court_name: Optional[str] = None
    legal_procedure: Optional[str] = None
    timeline: Optional[str] = None
    government_forms: List[str] = Field(default_factory=list)
    judgment_date: Optional[str] = None
    important_findings: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalise(cls, data):
        """Coerce imperfect model output into the expected shape."""

        if not isinstance(data, dict):
            return {}

        normalised = {}

        for field in _LIST_FIELDS:

            value = data.get(field)

            if value is None:
                value = []
            elif isinstance(value, str):
                value = [value] if value.strip() else []
            elif isinstance(value, list):
                value = [
                    str(item).strip()
                    for item in value
                    if item not in (None, "")
                ]
            else:
                value = []

            normalised[field] = value

        for field in _STR_FIELDS:

            value = data.get(field)

            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                value = None
            else:
                value = str(value).strip()

            normalised[field] = value

        return normalised


class DocumentMetadata(BaseModel):
    """Validated top-level legal document metadata record."""

    document_id: str
    file_name: str
    file_extension: str
    page_count: int
    document_metadata: dict
    processing_metadata: dict
    legal_metadata: dict
    extracted_information: Optional[LegalExtraction] = None
