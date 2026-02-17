import importlib
import os
import pkgutil
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-clara-tests-123")
os.environ.setdefault("DATABASE_URL", "postgresql://u:p@localhost/testdb")
os.environ.setdefault("COOKIE_SECURE", "false")

from clara.auth.models import User, Vault, VaultMembership, VaultSettings
from clara.auth.security import hash_password
from clara.base.model import Base
from clara.database import get_session as db_get_session
from clara.deps import get_session as deps_get_session
from clara.main import create_app


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    counters: dict[str, int] = {}

    class FakeRedis:
        def incr(self, key: str) -> int:
            counters[key] = counters.get(key, 0) + 1
            return counters[key]

        def expire(self, key: str, _: int) -> bool:
            counters.setdefault(key, 0)
            return True

    monkeypatch.setattr("clara.auth.api.redis_conn", FakeRedis())


def _import_model_modules() -> None:
    import clara

    for module in pkgutil.walk_packages(clara.__path__, f"{clara.__name__}."):
        if module.name.endswith(".models"):
            importlib.import_module(module.name)


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    _import_model_modules()
    test_engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield test_engine
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()


@pytest.fixture()
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[deps_get_session] = override_get_session
    app.dependency_overrides[db_get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
async def user(db_session: AsyncSession) -> User:
    test_user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("Password123!"),
    )
    db_session.add(test_user)
    await db_session.flush()
    return test_user


@pytest.fixture()
async def vault(db_session: AsyncSession, user: User) -> Vault:
    test_vault = Vault(name="Test Vault", owner_user_id=user.id)
    db_session.add(test_vault)
    await db_session.flush()

    user.default_vault_id = test_vault.id
    db_session.add(
        VaultMembership(
            user_id=user.id,
            vault_id=test_vault.id,
            role="owner",
        )
    )
    db_session.add(VaultSettings(vault_id=test_vault.id))
    await db_session.flush()
    return test_vault


@pytest.fixture()
async def authenticated_client(
    client: AsyncClient, user: User, vault: Vault
) -> AsyncClient:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Password123!"},
    )
    assert response.status_code == 200
    csrf_token = response.cookies.get("csrf_token") or client.cookies.get("csrf_token")
    if csrf_token:
        client.headers["x-csrf-token"] = csrf_token
    return client
