"""Password hashing and JWT token utilities."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from backend.app.core.config import config


def _prepare_password(password: str) -> bytes:
    """Pre-hash with SHA-256 so bcrypt's 72-byte limit is never exceeded."""

    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""

    return bcrypt.hashpw(
        _prepare_password(password),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""

    try:
        return bcrypt.checkpw(
            _prepare_password(password),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    role: str = "user",
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a signed JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token."""

    return jwt.decode(
        token,
        config.JWT_SECRET_KEY,
        algorithms=[config.JWT_ALGORITHM],
    )


def create_password_reset_token(subject: str) -> str:
    """Create a short-lived token for password reset flows."""

    return create_access_token(subject, role="reset", expires_minutes=30)
