"""LLM-based legal information extraction.

The configured LLM (Grok by xAI, or Gemini) extracts the structured legal
fields required by the project and returns a JSON object. The output is
validated with Pydantic. The model is instructed never to invent missing
legal facts or citations.
"""

from typing import Optional

from ai.data_pipeline.information_extraction.schemas import LegalExtraction
from ai.llm.provider import LLMClient, get_llm_client
from ai.rag.prompts.legal_prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_TEMPLATE,
)
from ai.security.guardrails import sanitize_document_text

MAX_EXTRACTION_CHARS = 15000


def extract_legal_information(
    document_text: str,
    client: Optional[LLMClient] = None,
) -> dict:
    """Extract and validate structured legal information using the LLM."""

    if not document_text or not document_text.strip():
        return LegalExtraction().model_dump()

    text = sanitize_document_text(
        document_text,
        max_chars=MAX_EXTRACTION_CHARS,
    )

    llm = client or get_llm_client()

    prompt = EXTRACTION_TEMPLATE.format(document_text=text)

    raw = llm.generate_json(
        prompt,
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
    )

    return LegalExtraction.model_validate(raw).model_dump()


def safe_extract_legal_information(
    document_text: str,
    client: Optional[LLMClient] = None,
) -> dict:
    """Extraction wrapper that never raises - returns empty fields on error.

    Keeps ingestion resilient when the LLM is unavailable or returns invalid
    JSON.
    """

    try:
        return extract_legal_information(document_text, client=client)
    except Exception:
        return LegalExtraction().model_dump()
