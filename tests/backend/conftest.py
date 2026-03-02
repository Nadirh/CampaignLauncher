import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Add backend source to path so imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "backend"))

from app.core.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncIterator[None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncIterator[AsyncSession]:
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    async with test_session_factory() as session:
        yield session
