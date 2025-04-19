from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth.services.settings import settings

_async_engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
_session_factory = async_sessionmaker(_async_engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """非同期セッションを取得する"""
    async with _session_factory() as session:
        yield session
