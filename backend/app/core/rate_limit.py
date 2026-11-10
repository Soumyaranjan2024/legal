"""A minimal in-memory sliding-window rate limiter.

ChromaDB is the only database in this project, but it is a vector store and
not suited for high-frequency counters. A small process-local limiter is
sufficient for protecting the API surface (login, chatbot, search).
"""

import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    """Sliding-window rate limiter keyed by an arbitrary string."""

    def __init__(self, max_requests: int, window_seconds: int):

        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self._hits = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> bool:
        """Record a hit and return True when still within the limit."""

        now = time.monotonic()
        window_start = now - self.window_seconds

        with self._lock:

            bucket = self._hits[key]

            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                return False

            bucket.append(now)

            return True

    def retry_after(self, key: str) -> int:
        """Seconds until the next request is allowed for ``key``."""

        with self._lock:

            bucket = self._hits.get(key)

            if not bucket:
                return 0

            elapsed = time.monotonic() - bucket[0]

            return max(0, int(self.window_seconds - elapsed) + 1)


# Shared limiters used by the API dependencies.
login_limiter = RateLimiter(max_requests=10, window_seconds=60)
chat_limiter = RateLimiter(max_requests=30, window_seconds=60)
search_limiter = RateLimiter(max_requests=60, window_seconds=60)
