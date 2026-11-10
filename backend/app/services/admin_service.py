"""Admin dashboard and reporting service."""

from collections import Counter
from datetime import datetime, timezone

from ai.rag.vector_database.document_store import LegalDocumentStore
from ai.rag.vector_database.vector_store import LegalVectorStore
from backend.app.core.config import config
from backend.app.db.chroma import collection_stats
from backend.app.db.repositories.chat_repository import ChatRepository
from backend.app.db.repositories.user_repository import UserRepository
from backend.app.schemas.admin import AdminStats, ReportItem, SystemReport


class AdminService:
    """Aggregate system statistics for the admin dashboard."""

    def __init__(
        self,
        user_repository=None,
        chat_repository=None,
        document_store=None,
        vector_store=None,
    ):

        self.users = user_repository or UserRepository()
        self.chats = chat_repository or ChatRepository()
        self.document_store = document_store or LegalDocumentStore()
        self.vector_store = vector_store or LegalVectorStore()

    # --- Stats ----------------------------------------------------------

    def stats(self) -> AdminStats:

        user_records = self.users.list_users()

        active = sum(
            1 for record in user_records
            if (record.get("metadata", {}) or {}).get("is_active", True)
        )

        chat_metadatas = (
            self.chats.collection.get(include=["metadatas"]).get("metadatas", [])
            or []
        )

        conversations = {
            (metadata or {}).get("conversation_id")
            for metadata in chat_metadatas
            if (metadata or {}).get("conversation_id")
        }

        return AdminStats(
            total_users=len(user_records),
            active_users=active,
            admin_users=self.users.count_by_role("admin"),
            total_documents=self.document_store.count(),
            total_chunks=self.vector_store.count_documents(),
            total_conversations=len(conversations),
            total_messages=self.chats.count(),
            llm_configured=config.llm_configured,
            llm_provider=config.llm_provider,
            embedding_model=config.EMBEDDING_MODEL,
            llm_model=config.llm_model,
            collections=collection_stats(),
        )

    # --- Reports --------------------------------------------------------

    def report(self) -> SystemReport:

        documents = self.document_store.list_documents()
        users = self.users.list_users()

        by_court = Counter()
        by_category = Counter()
        act_counter = Counter()

        for record in documents:

            metadata = record.get("metadata", {}) or {}

            if metadata.get("court_type"):
                by_court[metadata["court_type"]] += 1

            if metadata.get("legal_category"):
                by_category[metadata["legal_category"]] += 1

            if metadata.get("acts"):
                for act in str(metadata["acts"]).split(";"):
                    act = act.strip()
                    if act:
                        act_counter[act] += 1

        by_role = Counter(
            (record.get("metadata", {}) or {}).get("role", "user")
            for record in users
        )

        return SystemReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            stats=self.stats(),
            documents_by_court_type=dict(by_court),
            documents_by_category=dict(by_category),
            users_by_role=dict(by_role),
            top_acts=[
                ReportItem(label=label, value=count)
                for label, count in act_counter.most_common(10)
            ],
        )
