#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# テストユーザーを挿入または更新
# ------------------------------------------------------------------------------

set -euo pipefail
EMAIL="alice@example.com"
PASS="Pa55w0rd!"

# パスワードをハッシュ化
HASH=$(docker compose exec -T auth uv run python - <<'PY'
from passlib.context import CryptContext
ctx = CryptContext(schemes=["bcrypt"])
print(ctx.hash("Pa55w0rd!"))
PY
)

# ユーザーを挿入または更新
docker compose exec -T postgres psql -U postgres -d postgres <<SQL
INSERT INTO users (id, email, pw_hash)
VALUES ('11111111-1111-1111-1111-111111111111', '$EMAIL', '$HASH')
ON CONFLICT (email) DO UPDATE SET pw_hash = EXCLUDED.pw_hash;
SQL

echo "✅  Seeded user: $EMAIL / $PASS"
