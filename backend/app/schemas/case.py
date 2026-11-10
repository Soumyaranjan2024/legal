"""Legal case / judgment schemas."""

from typing import Any, List, Optional

from pydantic import BaseModel


class CaseSummary(BaseModel):

    document_id: str
    case_name: str = ""
    case_number: str = ""
    court_type: str = ""
    court_name: str = ""
    legal_category: str = ""
    judgment_date: str = ""
    acts: str = ""
    sections: str = ""
    source_url: Optional[str] = None
    file_name: str = ""


class CaseDetail(CaseSummary):

    important_findings: List[str] = []
    source_references: List[str] = []
    required_documents: List[str] = []
    legal_procedure: List[str] = []
    timeline: Optional[str] = None
    government_forms: List[str] = []
    metadata: dict[str, Any] = {}


class CaseListResponse(BaseModel):

    total: int
    cases: List[CaseSummary]


class CaseFilterOptions(BaseModel):

    court_types: List[str] = []
    categories: List[str] = []
