from datetime import UTC, datetime, timedelta

import argon2
import bcrypt
import jwt

from clara.config import get_settings

_ph = argon2.PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Argon2 hashes start with $argon2
    if hashed.startswith("$argon2"):
        try:
            return _ph.verify(hashed, plain)
        except argon2.exceptions.VerifyMismatchError:
            return False
    # Legacy bcrypt fallback
    if bcrypt.checkpw(plain.encode(), hashed.encode()):
        return True
    return False


def needs_rehash(hashed: str) -> bool:
    """True if hash is legacy bcrypt and should be upgraded to argon2."""
    return not hashed.startswith("$argon2")


def create_access_token(
    subject: str, expires_delta: timedelta | None = None
) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "access"},
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "refresh"},
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def _decode_token(token: str, expected_type: str) -> dict | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_access_token(token: str) -> dict | None:
    return _decode_token(token, "access")


def decode_refresh_token(token: str) -> dict | None:
    return _decode_token(token, "refresh")
