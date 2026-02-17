from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clara.auth.models import User, Vault, VaultMembership
from clara.auth.schemas import LoginRequest, RegisterRequest
from clara.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from clara.exceptions import ConflictError


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(
        self, data: RegisterRequest
    ) -> tuple[User, Vault, str, str]:
        existing = (
            await self.session.execute(
                select(User).where(User.email == data.email)
            )
        ).scalar_one_or_none()
        if existing:
            raise ConflictError("Email already registered")

        vault = Vault(name=f"{data.name or data.email}'s vault")
        self.session.add(vault)
        await self.session.flush()

        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
            default_vault_id=vault.id,
        )
        self.session.add(user)
        await self.session.flush()

        vault.owner_user_id = user.id

        membership = VaultMembership(
            user_id=user.id, vault_id=vault.id, role="owner"
        )
        self.session.add(membership)
        await self.session.flush()

        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        return user, vault, access, refresh

    async def login(self, data: LoginRequest) -> tuple[User, str, str]:
        user = (
            await self.session.execute(
                select(User).where(User.email == data.email)
            )
        ).scalar_one_or_none()
        if user is None or not verify_password(
            data.password, user.hashed_password
        ):
            raise ValueError("Invalid credentials")

        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        return user, access, refresh
