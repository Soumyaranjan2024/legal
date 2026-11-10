"""User records persisted in the ChromaDB ``users`` collection.

ChromaDB stores scalar metadata only, so the user record is kept as a JSON
document body while searchable fields (email, username, role, status) live in
metadata. There are no relational/transactional guarantees, so uniqueness is
enforced in this repository layer.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from ai.config.settings import settings
from ai.rag.vector_database.chroma_client import get_or_create_collection

_PLACEHOLDER_EMBEDDING = [0.0]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UserRepository:
    """CRUD operations for API users backed by ChromaDB."""

    def __init__(self, collection_name: Optional[str] = None):

        self.collection = get_or_create_collection(
            collection_name or settings.USERS_COLLECTION
        )

    # --- Helpers --------------------------------------------------------

    @staticmethod
    def _to_record(result: dict, index: int) -> dict:
        try:
            payload = json.loads(result["documents"][index])
        except (json.JSONDecodeError, TypeError, KeyError):
            payload = {}

        return {
            "user_id": result["ids"][index],
            "metadata": (result["metadatas"][index] or {}),
            "document": payload,
        }

    def _find(self, where: dict) -> List[dict]:
        result = self.collection.get(
            where=where,
            include=["documents", "metadatas"],
        )

        ids = result.get("ids", [])

        return [self._to_record(result, index) for index in range(len(ids))]

    # --- Queries --------------------------------------------------------

    def get_by_id(self, user_id: str) -> Optional[dict]:
        result = self.collection.get(ids=[user_id])

        if not result.get("ids"):
            return None

        return self._to_record(result, 0)

    def get_by_email(self, email: str) -> Optional[dict]:
        matches = self._find({"email": email.strip().lower()})
        return matches[0] if matches else None

    def get_by_username(self, username: str) -> Optional[dict]:
        matches = self._find({"username": username.strip()})
        return matches[0] if matches else None

    def list_users(self) -> List[dict]:
        result = self.collection.get(include=["documents", "metadatas"])
        ids = result.get("ids", [])
        return [self._to_record(result, index) for index in range(len(ids))]

    def count(self) -> int:
        return self.collection.count()

    def count_by_role(self, role: str) -> int:
        return len(self._find({"role": role}))

    def count_admins(self) -> int:
        return self.count_by_role("admin")

    # --- Mutations ------------------------------------------------------

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: str = "",
        role: str = "user",
    ) -> dict:
        """Create a user; raises ValueError on duplicate email/username."""

        email = email.strip().lower()
        username = username.strip()

        if self.get_by_email(email):
            raise ValueError("An account with this email already exists.")

        if self.get_by_username(username):
            raise ValueError("This username is already taken.")

        user_id = uuid.uuid4().hex
        created_at = _now()

        document = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": True,
            "created_at": created_at,
            "updated_at": created_at,
        }

        metadata = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": True,
            "password_hash": password_hash,
            "created_at": created_at,
            "updated_at": created_at,
        }

        self.collection.upsert(
            ids=[user_id],
            documents=[json.dumps(document, ensure_ascii=False)],
            embeddings=[_PLACEHOLDER_EMBEDDING],
            metadatas=[metadata],
        )

        return {"user_id": user_id, "metadata": metadata, "document": document}

    def update_user(self, user_id: str, **fields) -> Optional[dict]:
        """Update scalar fields on a user record."""

        record = self.get_by_id(user_id)

        if record is None:
            return None

        metadata = dict(record["metadata"])
        document = dict(record["document"])

        for key, value in fields.items():

            if value is None:
                continue

            metadata[key] = value
            document[key] = value

        metadata["updated_at"] = _now()
        document["updated_at"] = metadata["updated_at"]

        self.collection.upsert(
            ids=[user_id],
            documents=[json.dumps(document, ensure_ascii=False)],
            embeddings=[_PLACEHOLDER_EMBEDDING],
            metadatas=[metadata],
        )

        return {"user_id": user_id, "metadata": metadata, "document": document}

    def delete_user(self, user_id: str) -> bool:
        if not self.get_by_id(user_id):
            return False

        self.collection.delete(ids=[user_id])
        return True
