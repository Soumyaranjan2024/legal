"""Central configuration for the Legal Information Retrieval System.

All configuration is read from environment variables (see ``.env.example``).
Secrets such as ``XAI_API_KEY`` are NEVER hard-coded and are only ever read
on the backend / AI layer - never exposed to the frontend.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root: .../LEGAL_INFROMATION_RETRIEVAL_SYSTEM
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load variables from the project .env (never override real environment).
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_list(name: str, default: list) -> list:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """Application settings resolved from the environment."""

    # --- LLM ------------------------------------------------------------
    # Grok (xAI) is the preferred LLM. Groq and Gemini are supported as
    # alternatives when their respective keys are configured.
    XAI_API_KEY = _env_str("XAI_API_KEY", "")
    GROK_MODEL = _env_str("GROK_MODEL", "grok-2-latest")
    GROK_BASE_URL = _env_str("GROK_BASE_URL", "https://api.x.ai/v1")
    GROK_TEMPERATURE = _env_float("GROK_TEMPERATURE", 0.2)
    GROK_MAX_TOKENS = _env_int("GROK_MAX_TOKENS", 2000)

    GROQ_API_KEY = _env_str("GROQ_API_KEY", "")
    GROQ_MODEL = _env_str("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_BASE_URL = _env_str(
        "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
    )

    GEMINI_API_KEY = _env_str("GEMINI_API_KEY", "")
    GEMINI_MODEL = _env_str("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_BASE_URL = _env_str(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/models",
    )
    LLM_TIMEOUT_SECONDS = _env_float("LLM_TIMEOUT_SECONDS", 120)

    # --- Embeddings (BGE / E5 via Sentence Transformers) ----------------
    EMBEDDING_MODEL = _env_str("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    # --- ChromaDB (single, persistent, local vector database) -----------
    CHROMA_PERSIST_DIRECTORY = _env_str(
        "CHROMA_PERSIST_DIRECTORY",
        str(PROJECT_ROOT / "ai" / "storage" / "chroma_db"),
    )
    LEGAL_DOCUMENTS_COLLECTION = _env_str(
        "LEGAL_DOCUMENTS_COLLECTION", "legal_documents"
    )
    LEGAL_CHUNKS_COLLECTION = _env_str(
        "LEGAL_CHUNKS_COLLECTION", "legal_chunks"
    )
    USERS_COLLECTION = _env_str("USERS_COLLECTION", "users")
    CHAT_HISTORY_COLLECTION = _env_str(
        "CHAT_HISTORY_COLLECTION", "chat_history"
    )

    # --- Authentication -------------------------------------------------
    JWT_SECRET_KEY = _env_str(
        "JWT_SECRET_KEY", "change-this-secret-key-in-production"
    )
    JWT_ALGORITHM = _env_str("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = _env_int(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24
    )

    # --- Uploads --------------------------------------------------------
    UPLOAD_DIRECTORY = _env_str(
        "UPLOAD_DIRECTORY", str(PROJECT_ROOT / "datasets" / "raw")
    )
    MAX_UPLOAD_MB = _env_int("MAX_UPLOAD_MB", 50)
    ALLOWED_UPLOAD_EXTENSIONS = _env_list(
        "ALLOWED_UPLOAD_EXTENSIONS", [".pdf"]
    )

    # --- Retrieval ------------------------------------------------------
    TOP_K = _env_int("TOP_K", 10)
    MAX_TOP_K = _env_int("MAX_TOP_K", 20)
    CHUNK_SIZE = _env_int("CHUNK_SIZE", 1000)
    CHUNK_OVERLAP = _env_int("CHUNK_OVERLAP", 150)

    # --- Web-search fallback --------------------------------------------
    # When the legal knowledge base has nothing relevant, answer from web
    # search instead. WEB_SEARCH_MAX_DISTANCE is a loose "clearly irrelevant"
    # gate (cosine): a weak-but-clicked knowledge-base answer that turns out
    # uninformative still falls back to the web.
    WEB_SEARCH_ENABLED = _env_str("WEB_SEARCH_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    WEB_SEARCH_MAX_RESULTS = _env_int("WEB_SEARCH_MAX_RESULTS", 5)
    WEB_SEARCH_MAX_DISTANCE = _env_float("WEB_SEARCH_MAX_DISTANCE", 0.5)

    # --- OCR ------------------------------------------------------------
    TESSERACT_CMD = _env_str(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    )
    OCR_MIN_TEXT_LENGTH = _env_int("OCR_MIN_TEXT_LENGTH", 30)

    # --- Server / CORS --------------------------------------------------
    API_HOST = _env_str("API_HOST", "0.0.0.0")
    API_PORT = _env_int("API_PORT", 8000)
    CORS_ORIGINS = _env_list(
        "CORS_ORIGINS",
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
    )


settings = Settings()
