"""
pytest設定とフィクスチャ
"""
import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.config import get_settings

settings = get_settings()

# テスト用データベースURL（既存のDBを使用）
TEST_DATABASE_URL = settings.DATABASE_URL_ASYNC

# テスト用エンジン
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

# テスト用セッションメーカー
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """テスト用データベースセッション"""
    # テーブル作成
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # セッション提供
    async with TestSessionLocal() as session:
        yield session

    # クリーンアップ
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """テスト用HTTPクライアント"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
