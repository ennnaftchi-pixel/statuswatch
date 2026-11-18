from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db import get_session
from app.models import Base


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    # 1. Create a fresh in-memory SQLite database for each test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    # 2. Override the real Postgres session with our SQLite session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    # 3. Yield the test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 4. Clean up after the test
    app.dependency_overrides.clear()
