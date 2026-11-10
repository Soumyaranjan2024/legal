"""Chatbot and chat-history routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import enforce_rate_limit, get_current_user
from backend.app.core.logging_config import get_logger
from backend.app.core.rate_limit import chat_limiter
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationListResponse,
)
from backend.app.schemas.common import Message
from backend.app.schemas.user import UserPublic
from backend.app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chatbot"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
def ask(
    payload: ChatRequest,
    user: UserPublic = Depends(get_current_user),
) -> ChatResponse:
    """Ask a legal question and receive a source-grounded answer."""

    enforce_rate_limit(chat_limiter, f"chat:{user.user_id}")

    service = ChatService()

    try:
        result = service.ask(user.user_id, payload)
    except Exception as error:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate an answer: {error}",
        )

    return ChatResponse(**result)


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    user: UserPublic = Depends(get_current_user),
) -> ConversationListResponse:
    service = ChatService()
    conversations = service.list_conversations(user.user_id)

    return ConversationListResponse(
        total=len(conversations),
        conversations=conversations,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    user: UserPublic = Depends(get_current_user),
) -> ConversationDetail:
    service = ChatService()
    messages = service.get_conversation(user.user_id, conversation_id)

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return ConversationDetail(
        conversation_id=conversation_id,
        messages=messages,
    )


@router.delete("/conversations/{conversation_id}", response_model=Message)
def delete_conversation(
    conversation_id: str,
    user: UserPublic = Depends(get_current_user),
) -> Message:
    service = ChatService()
    deleted = service.delete_conversation(user.user_id, conversation_id)

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return Message(detail=f"Deleted {deleted} messages.")


@router.delete("/history", response_model=Message)
def clear_history(user: UserPublic = Depends(get_current_user)) -> Message:
    service = ChatService()
    deleted = service.clear(user.user_id)

    return Message(detail=f"Cleared {deleted} messages.")
