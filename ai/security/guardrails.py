"""Security guardrails.

Protects the RAG pipeline against prompt injection originating from uploaded
documents or user questions, and normalises untrusted text before it reaches
Grok.
"""

import re

# Common prompt-injection / instruction-override patterns.
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"forget\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*",
    r"assistant\s*:\s*",
    r"new\s+instructions?\s*:",
    r"override\s+(the\s+)?(system\s+)?prompt",
    r"reveal\s+(the\s+)?(system\s+)?prompt",
    r"print\s+(your\s+)?(system\s+)?(prompt|instructions)",
    r"act\s+as\s+(a\s+)?(different|new)\s+",
]

_INJECTION_REGEX = re.compile(
    "|".join(_INJECTION_PATTERNS),
    re.IGNORECASE,
)

MAX_QUESTION_LENGTH = 2000


def sanitize_question(question: str) -> str:
    """Validate and normalise a user question."""

    if not isinstance(question, str):
        raise TypeError("Question must be a string.")

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"Question is too long (max {MAX_QUESTION_LENGTH} characters)."
        )

    # Collapse whitespace but preserve content.
    question = re.sub(r"\s+", " ", question)

    # Neutralise obvious injection attempts inside the question.
    question = _INJECTION_REGEX.sub("[removed]", question)

    return question


def sanitize_document_text(text: str, max_chars: int = 20000) -> str:
    """Neutralise injection patterns in untrusted document text."""

    if not isinstance(text, str):
        return ""

    text = text[:max_chars]

    # Remove injected instruction-override lines so they cannot influence Grok.
    text = _INJECTION_REGEX.sub("[removed]", text)

    # Strip control characters that can be used to hide instructions.
    text = "".join(
        char for char in text
        if char in "\n\t" or ord(char) >= 32
    )

    return text


def is_suspicious(text: str) -> bool:
    """Return True if the text contains prompt-injection patterns."""

    if not isinstance(text, str):
        return False

    return bool(_INJECTION_REGEX.search(text))
