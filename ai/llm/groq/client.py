"""Groq client.

Groq exposes an OpenAI-compatible chat completions API. This client reuses the
request/parsing logic of :class:`GrokClient` and only swaps the endpoint,
credentials and model, so the RAG pipeline can run against Groq when a
``GROQ_API_KEY`` is configured.
"""

from typing import Optional

from openai import OpenAI

from ai.config.settings import settings
from ai.llm.grok.client import GrokClient


class GroqClient(GrokClient):
    """OpenAI-compatible chat client pointed at the Groq API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):

        self.api_key = api_key or settings.GROQ_API_KEY

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Add it to your project .env file."
            )

        self.model = model or settings.GROQ_MODEL
        self.temperature = settings.GROK_TEMPERATURE
        self.max_tokens = settings.GROK_MAX_TOKENS

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.GROQ_BASE_URL,
        )
