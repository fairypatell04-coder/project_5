import asyncio
import pytest
import pytest_asyncio





from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app


# -----------------------------
# Test database (SQLite async)
# -----------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

AsyncTestSession = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# -----------------------------
# Database setup / teardown
# -----------------------------
@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


# -----------------------------
# DB session fixture
# -----------------------------
@pytest_asyncio.fixture
async def session(setup_db):
    async with AsyncTestSession() as session:
        yield session


# -----------------------------
# FastAPI test client
# -----------------------------
@pytest.fixture
def client():
    return TestClient(app)
