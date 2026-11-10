"""User profile routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_current_user
from backend.app.db.repositories.chat_repository import ChatRepository
from backend.app.schemas.user import UserPublic, UserUpdateRequest
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
def get_profile(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return user


@router.put("/me", response_model=UserPublic)
def update_profile(
    payload: UserUpdateRequest,
    user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    service = UserService()

    updated = service.update_profile(user.user_id, payload.full_name or "")

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return updated


@router.get("/me/stats")
def my_stats(user: UserPublic = Depends(get_current_user)) -> dict:
    """Return usage statistics for the authenticated user."""

    chats = ChatRepository()

    return {
        "conversations": len(chats.list_conversations(user.user_id)),
        "messages": chats.count_by_user(user.user_id),
    }
