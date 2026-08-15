from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import(
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.db.base_class import Base
import app.models

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
  engine = create_async_engine(TEST_DATABASE_URL, echo=False)
  # Create tables in memory
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  async_session = async_sessionmaker(
      engine, class_=AsyncSession, expire_on_commit=False
  )
  async with async_session() as session:
    yield session
  # Cleanup tables after test completes
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
  await engine.dispose()