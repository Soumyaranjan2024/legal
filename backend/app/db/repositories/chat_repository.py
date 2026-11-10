"""Chat conversation and message records stored in ChromaDB.

Each message is stored as its own record so that appending a message never
requires rewriting a full conversation. Records are grouped into conversations
in the service layer.
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


class ChatRepository:
    """Store and query chat messages for users."""

    def __init__(self, collection_name: Optional[str] = None):

        self.collection = get_or_create_collection(
            collection_name or settings.CHAT_HISTORY_COLLECTION
        )

    @staticmethod
    def _to_record(result: dict, index: int) -> dict:
        try:
            payload = json.loads(result["documents"][index])
        except (json.JSONDecodeError, TypeError, KeyError):
            payload = {}

        return {
            "message_id": result["ids"][index],
            "metadata": (result["metadatas"][index] or {}),
            "document": payload,
        }

    def _query(self, where: dict) -> List[dict]:
        result = self.collection.get(
            where=where,
            include=["documents", "metadatas"],
        )

        ids = result.get("ids", [])
        records = [self._to_record(result, index) for index in range(len(ids))]

        # ChromaDB does not guarantee ordering; sort by creation time.
        records.sort(key=lambda item: item["metadata"].get("created_at", ""))

        return records

    # --- Mutations ------------------------------------------------------

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        conversation_id: Optional[str] = None,
        sources: Optional[list] = None,
        filters: Optional[dict] = None,
    ) -> dict:
        """Append a single chat message and return the stored record."""

        conversation_id = conversation_id or uuid.uuid4().hex
        message_id = uuid.uuid4().hex
        created_at = _now()

        document = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "filters": filters or {},
            "created_at": created_at,
        }

        metadata = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "created_at": created_at,
        }

        self.collection.upsert(
            ids=[message_id],
            documents=[json.dumps(document, ensure_ascii=False)],
            embeddings=[_PLACEHOLDER_EMBEDDING],
            metadatas=[metadata],
        )

        return {"message_id": message_id, "metadata": metadata, "document": document}

    def delete_conversation(self, user_id: str, conversation_id: str) -> int:
        """Delete every message in a user's conversation."""

        messages = self.list_messages(user_id, conversation_id)

        if not messages:
            return 0

        self.collection.delete(
            ids=[message["message_id"] for message in messages]
        )

        return len(messages)

    def clear_user(self, user_id: str) -> int:
        """Delete every message belonging to a user."""

        messages = self.list_messages(user_id)

        if not messages:
            return 0

        self.collection.delete(
            ids=[message["message_id"] for message in messages]
        )

        return len(messages)

    # --- Queries --------------------------------------------------------

    def list_messages(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
    ) -> List[dict]:
        if conversation_id:
            where = {
                "$and": [
                    {"user_id": user_id},
                    {"conversation_id": conversation_id},
                ]
            }
        else:
            where = {"user_id": user_id}

        return self._query(where)

    def get_conversation(self, user_id: str, conversation_id: str) -> List[dict]:
        return self._query({
            "$and": [
                {"user_id": user_id},
                {"conversation_id": conversation_id},
            ]
        })

    def list_conversations(self, user_id: str) -> List[dict]:
        """Group a user's messages into conversation summaries."""

        grouped: dict = {}

        for message in self.list_messages(user_id):

            key = message["metadata"].get("conversation_id", "")
            entry = grouped.setdefault(key, {
                "conversation_id": key,
                "message_count": 0,
                "last_message_at": "",
                "title": "",
            })

            entry["message_count"] += 1
            created_at = message["metadata"].get("created_at", "")
            entry["last_message_at"] = max(entry["last_message_at"], created_at)

            if not entry["title"] and message["metadata"].get("role") == "user":
                text = message["document"].get("content", "")
                entry["title"] = text[:80]

        conversations = list(grouped.values())
        conversations.sort(key=lambda item: item["last_message_at"], reverse=True)

        return conversations

    def count(self) -> int:
        return self.collection.count()

    def count_by_user(self, user_id: str) -> int:
        return len(self.list_messages(user_id))
