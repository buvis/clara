from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from clara.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


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
