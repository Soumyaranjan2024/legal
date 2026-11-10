"""Admin dashboard / reports schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AdminStats(BaseModel):

    total_users: int = 0
    active_users: int = 0
    admin_users: int = 0
    total_documents: int = 0
    total_chunks: int = 0
    total_conversations: int = 0
    total_messages: int = 0
    llm_configured: bool = False
    llm_provider: str = ""
    embedding_model: str = ""
    llm_model: str = ""
    collections: List[dict] = []


class ReportItem(BaseModel):

    label: str
    value: Any


class SystemReport(BaseModel):

    generated_at: str
    stats: AdminStats
    documents_by_court_type: Dict[str, int] = {}
    documents_by_category: Dict[str, int] = {}
    users_by_role: Dict[str, int] = {}
    top_acts: List[ReportItem] = []
