"""Keyless web-search fallback.

Used only when the local legal knowledge base has no relevant information for a
question. Retrieved legal documents remain the primary, authoritative source;
web results are a clearly-flagged fallback so the assistant can still answer.

Search uses the ``ddgs`` meta-search (no API key). Individual engines are
rate-limited unpredictably, so several backends are tried in order (Google
first) and their results are merged. ``web_search`` never raises - it returns an
empty list on any failure.
"""

from typing import Dict, List
import time

from ai.config.settings import settings

# Tried in order; the first backends that respond are used.
_BACKENDS = (
    "google",
    "bing",
    "duckduckgo",
    "yandex",
    "mojeek",
    "wikipedia",
)

# Engines are rate-limited unpredictably; retry the whole set once on failure.
_MAX_ATTEMPTS = 2
_RETRY_DELAY_SECONDS = 1.5
_MAX_SNIPPET_CHARS = 500


def web_search(query: str, max_results: int = None) -> List[Dict[str, str]]:
    """Return web results as ``{title, url, snippet}`` dicts."""

    if not query or not query.strip():
        return []

    limit = max_results or settings.WEB_SEARCH_MAX_RESULTS

    try:
        from ddgs import DDGS
    except Exception:
        return []

    for attempt in range(_MAX_ATTEMPTS):

        collected: List[Dict[str, str]] = []
        seen_urls = set()
        ddgs = DDGS()

        for backend in _BACKENDS:

            if len(collected) >= limit:
                break

            try:
                raw_results = ddgs.text(
                    query,
                    backend=backend,
                    max_results=limit,
                )
            except Exception:
                continue

            for item in raw_results or []:

                url = item.get("href") or item.get("url") or ""

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                collected.append({
                    "title": item.get("title") or url,
                    "url": url,
                    "snippet": (
                        item.get("body") or item.get("snippet") or ""
                    )[:_MAX_SNIPPET_CHARS],
                })

                if len(collected) >= limit:
                    break

        if collected:
            return collected

        if attempt < _MAX_ATTEMPTS - 1:
            time.sleep(_RETRY_DELAY_SECONDS)

    return []
