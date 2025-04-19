from __future__ import annotations

import time
from typing import Final

import redis.asyncio as redis
from jose import jwt

from auth.services.settings import settings

_PREFIX: Final[str] = "rt:"  # redis に保存するキーの prefix
redis_pool: redis.Redis = redis.from_url(settings.redis_url, decode_responses=False)

async def store_refresh_token(token: str) -> None:
    """リフレッシュトークンを保存する"""
    payload = jwt.get_unverified_claims(token)
    jti: str = payload["jti"]
    exp: int = payload["exp"]
    ttl = max(0, exp - int(time.time()))
    await redis_pool.setex(_PREFIX + jti, ttl, b"1")

async def revoke_refresh_token(token: str) -> None:
    """リフレッシュトークンを削除する"""
    jti = jwt.get_unverified_claims(token)["jti"]
    await redis_pool.delete(_PREFIX + jti)

async def is_refresh_token_valid(token: str) -> bool:
    """リフレッシュトークンが有効かどうかを確認する"""
    jti = jwt.get_unverified_claims(token)["jti"]
    return await redis_pool.exists(_PREFIX + jti)   # 該当のキーが存在するかどうかを確認

