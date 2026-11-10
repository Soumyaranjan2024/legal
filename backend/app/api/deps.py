"""Shared FastAPI dependencies: authentication, roles and rate limiting."""

from typing import Optional

from fastapi import Header, HTTPException, Request, status

from backend.app.core.logging_config import get_logger
from backend.app.core.rate_limit import RateLimiter
from backend.app.core.security import decode_access_token
from backend.app.schemas.user import UserPublic
from backend.app.services.user_service import UserService

logger = get_logger(__name__)


# Shared identity used when no valid token is supplied, so the platform is
# fully usable without creating an account or logging in.
GUEST_USER_ID = "guest-user"


def _guest_user() -> UserPublic:
    """Return the shared guest identity for unauthenticated requests."""

    return UserPublic(
        user_id=GUEST_USER_ID,
        username="guest",
        email="guest@localhost",
        full_name="Guest",
        role="user",
        is_active=True,
    )


def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> UserPublic:
    """Resolve the acting user.

    Login is optional: when a valid Bearer token is supplied the matching
    account is used, otherwise a shared guest identity is returned so every
    feature is reachable without signing in.
    """

    if not authorization or not authorization.lower().startswith("bearer "):
        return _guest_user()

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except Exception:
        return _guest_user()

    user_id = payload.get("sub")

    if not user_id:
        return _guest_user()

    user = UserService().get_by_id(user_id)

    if user is None or not user.is_active:
        return _guest_user()

    return user


def require_admin(user: UserPublic = None) -> UserPublic:
    """Ensure the authenticated user has the admin role."""

    if user is None or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return user


def client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def enforce_rate_limit(limiter: RateLimiter, key: str) -> None:
    """Raise HTTP 429 when the limiter rejects ``key``."""

    if not limiter.check(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down and try again shortly.",
            headers={"Retry-After": str(limiter.retry_after(key))},
        )
