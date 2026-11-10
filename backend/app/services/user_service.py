"""User account and authentication service."""

from typing import List, Optional

from backend.app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.app.db.repositories.user_repository import UserRepository
from backend.app.schemas.auth import RegisterRequest
from backend.app.schemas.user import UserPublic

VALID_ROLES = {"user", "admin"}


def to_public(record: dict) -> UserPublic:
    """Convert a stored user record into a safe public representation."""

    metadata = record.get("metadata", {}) or {}

    return UserPublic(
        user_id=record.get("user_id", metadata.get("user_id", "")),
        username=metadata.get("username", ""),
        email=metadata.get("email", ""),
        full_name=metadata.get("full_name", ""),
        role=metadata.get("role", "user"),
        is_active=bool(metadata.get("is_active", True)),
        created_at=metadata.get("created_at"),
        updated_at=metadata.get("updated_at"),
    )


class UserService:
    """Handle registration, login and profile management."""

    def __init__(self, repository: Optional[UserRepository] = None):

        self.repository = repository or UserRepository()

    # --- Registration / authentication ----------------------------------

    def register(self, payload: RegisterRequest) -> dict:
        """Create the first admin automatically, otherwise a normal user."""

        role = "admin" if self.repository.count() == 0 else "user"

        record = self.repository.create_user(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role=role,
        )

        return record

    def authenticate(self, email: str, password: str) -> Optional[dict]:
        record = self.repository.get_by_email(email)

        if record is None:
            return None

        password_hash = record["metadata"].get("password_hash", "")

        if not verify_password(password, password_hash):
            return None

        if not record["metadata"].get("is_active", True):
            raise PermissionError("This account has been deactivated.")

        return record

    def issue_token(self, record: dict) -> dict:
        from backend.app.core.config import config

        user = to_public(record)

        token = create_access_token(
            subject=user.user_id,
            role=user.role,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.model_dump(),
        }

    # --- Profile --------------------------------------------------------

    def get_by_id(self, user_id: str) -> Optional[UserPublic]:
        record = self.repository.get_by_id(user_id)
        return to_public(record) if record else None

    def list_users(self) -> List[UserPublic]:
        return [to_public(record) for record in self.repository.list_users()]

    def update_profile(self, user_id: str, full_name: str) -> Optional[UserPublic]:
        record = self.repository.update_user(user_id, full_name=full_name.strip())
        return to_public(record) if record else None

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> bool:
        record = self.repository.get_by_id(user_id)

        if record is None:
            return False

        if not verify_password(
            current_password, record["metadata"].get("password_hash", "")
        ):
            return False

        self.repository.update_user(
            user_id, password_hash=hash_password(new_password)
        )

        return True

    # --- Password reset -------------------------------------------------

    def create_reset_token(self, email: str) -> Optional[str]:
        record = self.repository.get_by_email(email)

        if record is None:
            return None

        return create_password_reset_token(record["user_id"])

    def reset_password(self, token: str, new_password: str) -> bool:
        try:
            payload = decode_access_token(token)
        except Exception:
            return False

        if payload.get("role") != "reset":
            return False

        user_id = payload.get("sub")

        if not user_id or not self.repository.get_by_id(user_id):
            return False

        self.repository.update_user(
            user_id, password_hash=hash_password(new_password)
        )

        return True

    # --- Admin operations ----------------------------------------------

    def admin_update(
        self,
        user_id: str,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        full_name: Optional[str] = None,
    ) -> Optional[UserPublic]:
        fields = {}

        if role is not None:
            if role not in VALID_ROLES:
                raise ValueError(f"Role must be one of {sorted(VALID_ROLES)}.")
            fields["role"] = role

        if is_active is not None:
            fields["is_active"] = is_active

        if full_name is not None:
            fields["full_name"] = full_name.strip()

        record = self.repository.update_user(user_id, **fields)

        return to_public(record) if record else None

    def delete_user(self, user_id: str) -> bool:
        return self.repository.delete_user(user_id)

    def count(self) -> int:
        return self.repository.count()
