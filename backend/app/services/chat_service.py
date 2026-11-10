"""Chatbot service: RAG answers plus conversation persistence."""

from typing import List, Optional

from backend.app.core.logging_config import get_logger
from backend.app.db.repositories.chat_repository import ChatRepository
from backend.app.schemas.chat import ChatRequest, ConversationSummary, MessagePublic
from backend.app.schemas.common import LegalSource
from backend.app.services.ai_runtime import get_rag_pipeline

logger = get_logger(__name__)

DISCLAIMER = (
    "This platform provides legal information, not professional legal advice. "
    "Please consult a qualified lawyer for advice on your specific situation."
)


def _build_where(
    court_type: Optional[str],
    court_name: Optional[str],
) -> Optional[dict]:
    """Translate API filters into a ChromaDB ``where`` clause."""

    clauses = []

    if court_type:
        clauses.append({"court_type": court_type})

    if court_name:
        clauses.append({"court_name": court_name})

    if not clauses:
        return None

    if len(clauses) == 1:
        return clauses[0]

    return {"$and": clauses}


class ChatService:
    """Answer legal questions with RAG and store the conversation."""

    def __init__(
        self,
        repository: Optional[ChatRepository] = None,
        rag_pipeline=None,
    ):

        self.repository = repository or ChatRepository()
        self._rag = rag_pipeline

    @property
    def rag(self):
        if self._rag is None:
            self._rag = get_rag_pipeline()
        return self._rag

    # --- Answering ------------------------------------------------------

    def ask(self, user_id: str, request: ChatRequest) -> dict:
        """Run the RAG pipeline and persist both messages."""

        where = _build_where(request.court_type, request.court_name)

        result = self.rag.generate_answer(
            request.question,
            top_k=request.top_k,
            where=where,
        )

        conversation_id = request.conversation_id

        user_message = self.repository.add_message(
            user_id=user_id,
            role="user",
            content=request.question,
            conversation_id=conversation_id,
            filters={
                "court_type": request.court_type,
                "court_name": request.court_name,
                "acts": request.acts,
                "top_k": request.top_k,
            },
        )

        conversation_id = user_message["metadata"]["conversation_id"]

        assistant_message = self.repository.add_message(
            user_id=user_id,
            role="assistant",
            content=result["answer"],
            conversation_id=conversation_id,
            sources=result.get("sources", []),
        )

        return {
            "conversation_id": conversation_id,
            "question": result["question"],
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "retrieved_count": result.get("retrieved_count", 0),
            "disclaimer": DISCLAIMER,
            "message_id": assistant_message["message_id"],
        }

    # --- History --------------------------------------------------------

    def list_conversations(self, user_id: str) -> List[ConversationSummary]:

        return [
            ConversationSummary(**item)
            for item in self.repository.list_conversations(user_id)
        ]

    def get_conversation(
        self,
        user_id: str,
        conversation_id: str,
    ) -> List[MessagePublic]:

        messages = self.repository.get_conversation(user_id, conversation_id)

        return [
            MessagePublic(
                message_id=message["message_id"],
                conversation_id=message["metadata"].get("conversation_id", ""),
                role=message["metadata"].get("role", ""),
                content=message["document"].get("content", ""),
                sources=[
                    LegalSource(**source)
                    for source in message["document"].get("sources", [])
                ],
                created_at=message["metadata"].get("created_at"),
            )
            for message in messages
        ]

    def delete_conversation(self, user_id: str, conversation_id: str) -> int:
        return self.repository.delete_conversation(user_id, conversation_id)

    def clear(self, user_id: str) -> int:
        return self.repository.clear_user(user_id)
