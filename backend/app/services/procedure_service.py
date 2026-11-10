"""Legal procedure service derived from Grok extractions."""

from typing import List, Optional

from ai.rag.vector_database.document_store import LegalDocumentStore
from backend.app.schemas.procedure import Procedure
from backend.app.services.case_service import _as_list


class ProcedureService:
    """Surface legal procedures, documents and forms extracted by Grok."""

    def __init__(self, document_store: Optional[LegalDocumentStore] = None):

        self.document_store = document_store or LegalDocumentStore()

    def _procedure_records(self) -> List[dict]:
        """Documents that contain procedure/document/form information."""

        procedures = []

        for record in self.document_store.list_documents():

            extracted = (record.get("document", {}) or {}).get(
                "extracted_information", {}
            ) or {}

            if (
                _as_list(extracted.get("legal_procedure"))
                or _as_list(extracted.get("required_documents"))
                or _as_list(extracted.get("government_forms"))
            ):
                procedures.append(record)

        return procedures

    @staticmethod
    def _to_procedure(record: dict) -> Procedure:

        metadata = record.get("metadata", {}) or {}
        extracted = (record.get("document", {}) or {}).get(
            "extracted_information", {}
        ) or {}

        return Procedure(
            document_id=record["document_id"],
            title=metadata.get("title", "") or metadata.get("file_name", ""),
            legal_category=metadata.get("legal_category", ""),
            acts=metadata.get("acts", ""),
            sections=metadata.get("sections", ""),
            court_name=metadata.get("court_name", ""),
            legal_procedure=_as_list(extracted.get("legal_procedure")),
            required_documents=_as_list(extracted.get("required_documents")),
            government_forms=_as_list(extracted.get("government_forms")),
            timeline=extracted.get("timeline"),
            source_url=metadata.get("source_url") or None,
            file_name=metadata.get("file_name", ""),
        )

    def list_procedures(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Procedure]:

        procedures = []

        for record in self._procedure_records():

            procedure = self._to_procedure(record)

            if category and procedure.legal_category != category:
                continue

            if query:
                haystack = " ".join(
                    procedure.legal_procedure
                    + procedure.required_documents
                    + [procedure.title, procedure.acts]
                ).lower()

                if query.lower() not in haystack:
                    continue

            procedures.append(procedure)

        return procedures

    def get_procedure(self, document_id: str) -> Optional[Procedure]:

        record = self.document_store.get_document(document_id)

        if record is None:
            return None

        return self._to_procedure(record)
