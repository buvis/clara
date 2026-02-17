import uuid

from fastapi import APIRouter, HTTPException, Request, Response

from clara.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserRead,
)
from clara.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from clara.auth.service import AuthService
from clara.config import get_settings
from clara.deps import CurrentUser, Db
from clara.middleware import generate_csrf_token
from clara.redis import redis_conn

router = APIRouter()

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60  # seconds


def _check_login_rate(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"rate:login:{ip}"
    count = redis_conn.incr(key)
    if count == 1:
        redis_conn.expire(key, LOGIN_RATE_WINDOW)
    if count > LOGIN_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many login attempts")


def _set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    settings = get_settings()
    for name, value, max_age in [
        ("access_token", access, settings.access_token_expire_minutes * 60),
        ("refresh_token", refresh, settings.refresh_token_expire_days * 86400),
    ]:
        response.set_cookie(
            key=name,
            value=value,
            max_age=max_age,
            httponly=settings.cookie_httponly,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain,
        )
    # CSRF token — readable by JS (httponly=False)
    response.set_cookie(
        key="csrf_token",
        value=generate_csrf_token(),
        max_age=settings.access_token_expire_minutes * 60,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, db: Db, response: Response):
    svc = AuthService(db)
    user, vault, access, refresh = await svc.register(body)
    _set_auth_cookies(response, access, refresh)
    return AuthResponse(
        user=UserRead.model_validate(user),
        access_token=access,
        vault_id=vault.id,
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: Db, response: Response, request: Request):
    _check_login_rate(request)
    svc = AuthService(db)
    user, access, refresh = await svc.login(body)
    _set_auth_cookies(response, access, refresh)
    return AuthResponse(
        user=UserRead.model_validate(user),
        access_token=access,
        vault_id=user.default_vault_id,
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(request: Request, db: Db, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    payload = decode_refresh_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    from clara.auth.models import User
    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    _set_auth_cookies(response, access, new_refresh)
    return AuthResponse(
        user=UserRead.model_validate(user),
        access_token=access,
        vault_id=user.default_vault_id,
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"ok": True}


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser):
    return UserRead.model_validate(user)
