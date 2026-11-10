"""Legal procedure schemas."""

from typing import List, Optional

from pydantic import BaseModel


class Procedure(BaseModel):

    document_id: str
    title: str = ""
    legal_category: str = ""
    acts: str = ""
    sections: str = ""
    court_name: str = ""
    legal_procedure: List[str] = []
    required_documents: List[str] = []
    government_forms: List[str] = []
    timeline: Optional[str] = None
    source_url: Optional[str] = None
    file_name: str = ""


class ProcedureListResponse(BaseModel):

    total: int
    procedures: List[Procedure]
