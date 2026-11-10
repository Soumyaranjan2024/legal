"""Chat / chatbot schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field

from backend.app.schemas.common import LegalSource


class ChatRequest(BaseModel):

    question: str = Field(min_length=2, max_length=2000)
    conversation_id: Optional[str] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    court_type: Optional[str] = None
    court_name: Optional[str] = None
    acts: Optional[str] = None


class ChatResponse(BaseModel):

    conversation_id: str
    question: str
    answer: str
    sources: List[LegalSource] = []
    retrieved_count: int = 0
    disclaimer: str


class MessagePublic(BaseModel):

    message_id: str
    conversation_id: str
    role: str
    content: str
    sources: List[LegalSource] = []
    created_at: Optional[str] = None


class ConversationSummary(BaseModel):

    conversation_id: str
    title: str = ""
    message_count: int = 0
    last_message_at: Optional[str] = None


class ConversationListResponse(BaseModel):

    total: int
    conversations: List[ConversationSummary]


class ConversationDetail(BaseModel):

    conversation_id: str
    messages: List[MessagePublic]
