import os

# Must be set before any app import — pydantic-settings reads on first Settings() call
os.environ.setdefault("PIPEFY_TOKEN", "test-token")
os.environ.setdefault("PIPEFY_PIPE_ID", "1")
os.environ.setdefault("PIPEFY_WEBHOOK_SECRET", "test-webhook-secret")

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_session
from app.pipefy.dependencies import get_pipefy_client
from app.main import app  # noqa: F401 — triggers model registrations before create_all

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_WEBHOOK_SECRET = "test-webhook-secret"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def mock_pipefy():
    mock = MagicMock()
    mock.create_card = AsyncMock(return_value="card_999")
    mock.update_card_fields = AsyncMock(return_value=True)
    return mock


@pytest_asyncio.fixture
async def client(test_engine, mock_pipefy):
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_session():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_pipefy_client] = lambda: mock_pipefy

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
