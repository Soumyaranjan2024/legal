"""Lightweight validation of Grok-generated legal answers.

Checks that section references used in an answer are grounded in the retrieved
context, flagging potential unsupported citations. This is a guardrail, not a
replacement for human legal review.
"""

import re

_SECTION_REGEX = re.compile(r"\bsections?\s+(\d+[A-Za-z]?)", re.IGNORECASE)


def _extract_sections(text: str) -> set:
    return {match.lower() for match in _SECTION_REGEX.findall(text or "")}


def validate_answer(answer: str, context: str) -> dict:
    """Compare section references in the answer against the context.

    Returns a dict with ``is_grounded`` and any ``unsupported_sections``.
    """

    answer_sections = _extract_sections(answer)
    context_sections = _extract_sections(context)

    unsupported = sorted(answer_sections - context_sections)

    return {
        "is_grounded": len(unsupported) == 0,
        "unsupported_sections": unsupported,
        "answer_section_count": len(answer_sections),
    }
