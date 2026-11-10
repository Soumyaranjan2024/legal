import re


def _unique(values):
    """Remove duplicates while preserving order."""
    return list(dict.fromkeys(values))


def extract_legal_entities(text: str) -> dict:
    """Extract basic legal entities from Indian legal documents."""

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return {
            "acts": [],
            "sections": [],
            "dates": [],
            "courts": [],
            "case_references": []
        }

    # Normalize whitespace to remove PDF line breaks
    text = re.sub(r"\s+", " ", text)

    # 1. Extract known Indian Act names
    known_acts = [
        "Information Technology Act, 2000",
        "Information Technology (Amendment) Act, 2008",
        "Indian Evidence Act, 1872",
        "Books Evidence Act, 1891",
        "Reserve Bank of India Act, 1934",
        "Income-tax Act, 1961",
        "Telecom Regulatory Authority of India Act, 1997",
        "Finance Act, 2017",
        "Limitation Act, 1963",
        "Copyright Act, 1957",
        "Patents Act, 1970",
        "Negotiable Instruments Act, 1881",
        "Powers-of-Attorney Act, 1882",
        "Indian Trust Act, 1882",
        "Indian Succession Act, 1925"
    ]

    acts = []

    for act in known_acts:
        pattern = re.escape(act)
        if re.search(pattern, text, re.IGNORECASE):
            acts.append(act)

    # 2. Extract section references
    section_pattern = (
        r"\bsections?\s+\d+[A-Z]?"
        r"(?:\s*(?:,|and|&)\s*\d+[A-Z]?)*"
    )

    section_matches = re.findall(
        section_pattern,
        text,
        re.IGNORECASE
    )

    sections = [
        item.strip()
        for item in section_matches
        if not item.split()[0].isupper()
    ]

    # 3. Extract dates
    date_pattern = (
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|"
        r"July|August|September|October|November|December)"
        r"\s+\d{4})\b"
    )

    dates = re.findall(date_pattern, text, re.IGNORECASE)

    # 4. Extract court names
    court_pattern = (
        r"\b(?:Supreme Court of India|"
        r"High Court of [A-Z][A-Za-z\s]+?|"
        r"District Court(?:s)?|"
        r"Sessions Court|"
        r"Family Court|"
        r"Commercial Court)\b"
    )

    courts = re.findall(court_pattern, text, re.IGNORECASE)

    # 5. Extract common Indian case citations
    case_pattern = (
        r"\b(?:AIR\s+\d{4}\s+\w+\s+\d+|"
        r"\(\d{4}\)\s+\d+\s+SCC\s+\d+|"
        r"\d{4}\s+SCC\s+OnLine\s+\w+\s+\d+)\b"
    )

    case_references = re.findall(
        case_pattern,
        text,
        re.IGNORECASE
    )

    return {
        "acts": _unique(acts),
        "sections": _unique(sections),
        "dates": _unique(dates),
        "courts": _unique(courts),
        "case_references": _unique(case_references)
    }