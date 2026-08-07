"""Pytest configuration and async test fixtures."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from nexuscrm.core.db import Base, get_db
from nexuscrm.main import app
from nexuscrm.core.security import get_password_hash
from nexuscrm.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create in-memory database tables for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create async test HTTP client overriding get_db dependency."""
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client, db_session):
    """Fixture providing authentication bearer headers."""
    test_user = User(
        email="testuser@nexuscrm.io",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role=UserRole.SALES_REP,
    )
    db_session.add(test_user)
    await db_session.commit()

    # Get Auth Token
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@nexuscrm.io", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
