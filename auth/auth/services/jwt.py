from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jose import jwt, jwk

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
PRIVATE_KEY_PATH = Path("/run/secrets/auth_private_key.pem")

_PRIVATE_KEY_PEM: bytes = PRIVATE_KEY_PATH.read_bytes()

# --- 署名 -----------------------------------------------------
def _now() -> datetime: return datetime.now(timezone.utc)

def create_access_token(subject: str, **extra: Any) -> str:
    payload = {
        "sub": subject,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "jti": str(uuid.uuid4()),
        **extra,
    }
    return jwt.encode(payload, _PRIVATE_KEY_PEM, algorithm=ALGORITHM)

def create_refresh_token(subject: str, version: int) -> str:
    payload = {
        "sub": subject,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        "jti": str(uuid.uuid4()),
        "ver": version,
    }
    return jwt.encode(payload, _PRIVATE_KEY_PEM, algorithm=ALGORITHM)

# --- 公開鍵 (JWKS 用) ----------------------------------------
_PRIVATE_JWK = jwk.construct(_PRIVATE_KEY_PEM, ALGORITHM)
PUBLIC_JWK_DICT: dict[str, Any] = _PRIVATE_JWK.to_dict()  # ← これを JWKS に流用
