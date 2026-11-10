"""LLM provider selection.

Grok (xAI) is the preferred provider. Groq and Gemini are used as fallbacks
when only their respective keys are configured, so the system still generates
answers.
"""

from typing import Union

from ai.config.settings import settings
from ai.llm.gemini.client import GeminiClient
from ai.llm.grok.client import GrokClient
from ai.llm.groq.client import GroqClient

LLMClient = Union[GrokClient, GroqClient, GeminiClient]


def llm_provider_name() -> str:
    """Return the active provider name, or an empty string if none is set."""

    if settings.XAI_API_KEY:
        return "grok"

    if settings.GROQ_API_KEY:
        return "groq"

    if settings.GEMINI_API_KEY:
        return "gemini"

    return ""


def get_llm_client() -> LLMClient:
    """Build the LLM client for the configured provider."""

    provider = llm_provider_name()

    if provider == "grok":
        return GrokClient()

    if provider == "groq":
        return GroqClient()

    if provider == "gemini":
        return GeminiClient()

    raise ValueError(
        "No LLM API key is configured. Set XAI_API_KEY (Grok), GROQ_API_KEY "
        "(Groq) or GEMINI_API_KEY (Gemini) in your project .env file."
    )
