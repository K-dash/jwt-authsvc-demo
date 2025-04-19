from __future__ import annotations

import json
from datetime import timedelta
from typing import Final

import redis.asyncio as redis

from auth.services.settings import settings

_REFRESH_PREFIX: Final[str] = "rt:"

redis_pool: redis.Redis = redis.from_url(settings.redis_url, decode_responses=False)

async def store_refresh_token(token: str) -> None:
    """Store RT's jti as key with TTL."""
    from jose import jwt
    payload = jwt.get_unverified_claims(token)
    jti: str = payload["jti"]
    exp: int = payload["exp"]
    ttl = max(0, exp - int(__import__("time").time()))
    await redis_pool.setex(_REFRESH_PREFIX + jti, ttl, "1")

async def is_refresh_token_valid(jti: str) -> bool:
    return not await redis_pool.exists(_REFRESH_PREFIX + jti)
