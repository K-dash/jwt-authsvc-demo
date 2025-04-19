from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jose import jwt, jwk, JWTError
from cryptography.hazmat.primitives import serialization

# ---------------------------------------------------------------------------#
ALGORITHM = "RS256"
KID       = "202504-key"                  # ローテーション識別子
ISS       = "authsvc.example.com"         # 発行者
AUD       = "backend-api"                 # トークン宛先
# ---------------------------------------------------------------------------#
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS   = 30
PRIVATE_KEY_PATH            = Path("/run/secrets/auth_private_key.pem")

_PRIVATE_KEY_PEM: bytes = PRIVATE_KEY_PATH.read_bytes()

def _now() -> datetime:
    """UTC 現在時刻を返す"""
    return datetime.now(timezone.utc)

def _base_claims(sub: str) -> dict[str, Any]:
    """iss / aud / sub / iat / jti の共通クレーム"""
    return {
        "iss": ISS,
        "aud": AUD,
        "sub": sub,
        "iat": int(_now().timestamp()),
        "jti": str(uuid.uuid4()),
    }

def create_access_token(sub: str, **extra: Any) -> str:
    """アクセストークンを作成する"""
    payload = _base_claims(sub) | {
        "exp": int((_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        **extra,
    }
    headers = {"kid": KID} # ヘッダに kid を追加することで、ローテーションをサポート
    return jwt.encode(payload, _PRIVATE_KEY_PEM, algorithm=ALGORITHM, headers=headers)

def create_refresh_token(sub: str, ver: int) -> str:
    """リフレッシュトークンを作成"""
    payload = _base_claims(sub) | {
        "ver": ver,
        "exp": int((_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
    }
    headers = {"kid": KID} # ヘッダに kid を追加することで、ローテーションをサポート
    return jwt.encode(payload, _PRIVATE_KEY_PEM, algorithm=ALGORITHM, headers=headers)

# -----------------------------------------------------------
# 公開鍵 PEM を生成
_public_key = serialization.load_pem_private_key(_PRIVATE_KEY_PEM, password=None).public_key()
_PUBLIC_KEY_PEM: bytes = _public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# 公開鍵 JWK（JWKS 配信用）
_PUBLIC_JWK = jwk.construct(_PUBLIC_KEY_PEM, ALGORITHM)
PUBLIC_JWK_DICT = _PUBLIC_JWK.to_dict() | {
    "kid": KID,         # ローテーション識別子
    "use": "sig",       # 使用目的
    "alg": ALGORITHM,   # アルゴリズム
}

# -----------------------------------------------------------
def decode_token(token: str, *, verify_exp: bool = True) -> dict[str, Any]:
    """
    署名・exp・aud・iss を検証してペイロードを返す
    invalid なら ValueError("invalid_token")
    """
    try:
        return jwt.decode(
            token,
            _PUBLIC_KEY_PEM,            # 公開鍵
            algorithms=[ALGORITHM],     # アルゴリズム
            issuer=ISS,                 # iss 検証 （iss は発行者）
            audience=AUD,               # aud 検証 （aud はトークン宛先）
            options={"verify_exp": verify_exp},
        )
    except JWTError as exc:
        raise ValueError("invalid_token") from exc
