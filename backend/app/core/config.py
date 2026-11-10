"""Backend configuration.

Reuses the central AI settings (single source of truth) and adds API-specific
values. Secrets are only ever read on the backend - never exposed to the
frontend.
"""

import sys
from pathlib import Path

# Ensure the project root is importable so the ``ai`` package can be used.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.config.settings import settings  # noqa: E402
from ai.llm.provider import llm_provider_name  # noqa: E402


class Config:
    """API configuration derived from the shared settings object."""

    PROJECT_ROOT = PROJECT_ROOT
    VERSION = "1.0.0"
    API_PREFIX = "/api"

    # LLM (Grok by xAI, with Groq or Gemini as fallbacks)
    XAI_API_KEY = settings.XAI_API_KEY
    GROK_MODEL = settings.GROK_MODEL
    GROQ_API_KEY = settings.GROQ_API_KEY
    GROQ_MODEL = settings.GROQ_MODEL
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    GEMINI_MODEL = settings.GEMINI_MODEL

    # Database
    CHROMA_PERSIST_DIRECTORY = settings.CHROMA_PERSIST_DIRECTORY

    # Embeddings
    EMBEDDING_MODEL = settings.EMBEDDING_MODEL

    # Auth
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    JWT_ALGORITHM = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # Uploads
    UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY
    MAX_UPLOAD_MB = settings.MAX_UPLOAD_MB
    ALLOWED_UPLOAD_EXTENSIONS = settings.ALLOWED_UPLOAD_EXTENSIONS

    # Retrieval
    TOP_K = settings.TOP_K
    MAX_TOP_K = settings.MAX_TOP_K

    # CORS
    CORS_ORIGINS = settings.CORS_ORIGINS

    @property
    def llm_provider(self) -> str:
        """Active LLM provider: "grok", "groq", "gemini" or "" when none is set."""

        return llm_provider_name()

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_provider)

    @property
    def llm_model(self) -> str:
        """Model name of the active provider."""

        if self.llm_provider == "grok":
            return self.GROK_MODEL

        if self.llm_provider == "groq":
            return self.GROQ_MODEL

        return self.GEMINI_MODEL


config = Config()
