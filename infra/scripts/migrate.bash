#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Alembic マイグレーションを auth コンテナ内で実行
# -----------------------------------------------------------------------------
set -euo pipefail

# ルートに移動
cd auth

if [[ ! -f alembic.ini ]]; then
    echo "alembic.ini not found in $(pwd)" >&2
    exit 1
fi

# フォールバックとしてコンテナ内で設定された環境変数を使用
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:postgres@postgres:5432/postgres}"

echo "Running Alembic migrations using uv run..."
uv run alembic upgrade head
