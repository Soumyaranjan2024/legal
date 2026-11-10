"""User-facing schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    """Safe representation of a user (never contains the password hash)."""

    user_id: str
    username: str
    email: str
    full_name: str = ""
    role: str = "user"
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserUpdateRequest(BaseModel):

    full_name: Optional[str] = Field(default=None, max_length=120)


class AdminUserUpdateRequest(BaseModel):

    role: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = Field(default=None, max_length=120)


class UserListResponse(BaseModel):

    total: int
    users: List[UserPublic]
