from __future__ import annotations

from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import os, sys

sys.path.append(str(os.path.abspath(os.path.join(__file__, "../../.."))))
from auth.services.settings import settings
from auth.models import user  # noqa: E402

# 設定ファイルの読み込み
config = context.config
fileConfig(config.config_file_name)

# target_metadata は Alembic が追跡するテーブルを指定する
from sqlalchemy.orm import DeclarativeMeta
from auth.models.user import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    connectable: AsyncEngine = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool
    )

    def do_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    import asyncio
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
