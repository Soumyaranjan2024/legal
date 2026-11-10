"""Legal case / judgment service derived from stored document records."""

from typing import List, Optional

from ai.rag.vector_database.document_store import LegalDocumentStore
from backend.app.schemas.case import (
    CaseDetail,
    CaseFilterOptions,
    CaseSummary,
)


def _as_list(value) -> List[str]:
    """Coerce a Grok extraction field into a clean list of strings."""

    if not value:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if item]

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    return [str(value)]


class CaseService:
    """Expose judgments (Supreme Court / High Court) from the knowledge base."""

    def __init__(self, document_store: Optional[LegalDocumentStore] = None):

        self.document_store = document_store or LegalDocumentStore()

    def _case_records(self) -> List[dict]:
        """Documents that look like judgments (court or case metadata present)."""

        cases = []

        for record in self.document_store.list_documents():

            metadata = record.get("metadata", {}) or {}

            if metadata.get("court_type") or metadata.get("case_name"):
                cases.append(record)

        return cases

    @staticmethod
    def _summary(record: dict) -> CaseSummary:

        metadata = record.get("metadata", {}) or {}

        return CaseSummary(
            document_id=record["document_id"],
            case_name=metadata.get("case_name", ""),
            case_number=metadata.get("case_number", ""),
            court_type=metadata.get("court_type", ""),
            court_name=metadata.get("court_name", ""),
            legal_category=metadata.get("legal_category", ""),
            judgment_date=metadata.get("judgment_date", ""),
            acts=metadata.get("acts", ""),
            sections=metadata.get("sections", ""),
            source_url=metadata.get("source_url") or None,
            file_name=metadata.get("file_name", ""),
        )

    def list_cases(
        self,
        court_type: Optional[str] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[CaseSummary]:

        cases = []

        for record in self._case_records():

            summary = self._summary(record)

            if court_type and summary.court_type != court_type:
                continue

            if category and summary.legal_category != category:
                continue

            if query:
                haystack = " ".join([
                    summary.case_name,
                    summary.case_number,
                    summary.acts,
                    summary.court_name,
                ]).lower()

                if query.lower() not in haystack:
                    continue

            cases.append(summary)

        return cases

    def get_case(self, document_id: str) -> Optional[CaseDetail]:

        record = self.document_store.get_document(document_id)

        if record is None:
            return None

        summary = self._summary(record)
        extracted = (record.get("document", {}) or {}).get(
            "extracted_information", {}
        ) or {}

        return CaseDetail(
            **summary.model_dump(),
            important_findings=_as_list(extracted.get("important_findings")),
            source_references=_as_list(extracted.get("source_references")),
            required_documents=_as_list(extracted.get("required_documents")),
            legal_procedure=_as_list(extracted.get("legal_procedure")),
            timeline=extracted.get("timeline"),
            government_forms=_as_list(extracted.get("government_forms")),
            metadata=record.get("metadata", {}) or {},
        )

    def filter_options(self) -> CaseFilterOptions:

        court_types = set()
        categories = set()

        for record in self._case_records():

            metadata = record.get("metadata", {}) or {}

            if metadata.get("court_type"):
                court_types.add(metadata["court_type"])

            if metadata.get("legal_category"):
                categories.add(metadata["legal_category"])

        return CaseFilterOptions(
            court_types=sorted(court_types),
            categories=sorted(categories),
        )
