from fastapi import APIRouter, Response

from clara.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserRead,
)
from clara.auth.service import AuthService
from clara.config import get_settings
from clara.deps import CurrentUser, Db

router = APIRouter()


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
async def login(body: LoginRequest, db: Db, response: Response):
    svc = AuthService(db)
    user, access, refresh = await svc.login(body)
    _set_auth_cookies(response, access, refresh)
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
