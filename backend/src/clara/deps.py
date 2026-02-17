import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clara.auth.models import User, VaultMembership
from clara.auth.security import decode_access_token
from clara.database import get_session

Db = Annotated[AsyncSession, Depends(get_session)]


async def _extract_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_current_user(
    token: str = Depends(_extract_token),
    session: AsyncSession = Depends(get_session),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = await session.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_vault_membership(
    vault_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VaultMembership:
    stmt = select(VaultMembership).where(
        VaultMembership.user_id == user.id,
        VaultMembership.vault_id == vault_id,
    )
    membership = (await session.execute(stmt)).scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this vault",
        )
    return membership


CurrentUser = Annotated[User, Depends(get_current_user)]
VaultAccess = Annotated[VaultMembership, Depends(get_vault_membership)]


def require_role(*roles: str):
    """Dependency factory: checks membership role against allowed roles."""

    async def _check(
        membership: VaultMembership = Depends(get_vault_membership),
    ) -> VaultMembership:
        if membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(roles)}",
            )
        return membership

    return Depends(_check)
