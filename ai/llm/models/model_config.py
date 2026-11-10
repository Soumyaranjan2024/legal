"""Model configuration for the legal information system.

Centralises model identifiers so every component uses consistent, compatible
models (Grok for the LLM, BGE/E5 for embeddings).
"""

from ai.config.settings import settings

# LPU-free, Grok-only configuration.
GROK_MODEL = settings.GROK_MODEL
GROK_BASE_URL = settings.GROK_BASE_URL
EMBEDDING_MODEL = settings.EMBEDDING_MODEL


def get_model_config() -> dict:
    """Return the active model configuration (no secrets included)."""

    return {
        "llm_provider": "xai-grok",
        "grok_model": GROK_MODEL,
        "grok_base_url": GROK_BASE_URL,
        "embedding_model": EMBEDDING_MODEL,
        "vector_database": "chromadb",
    }
