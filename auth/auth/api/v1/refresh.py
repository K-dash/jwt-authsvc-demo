from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services.db import get_session
from auth.services.jwt import create_access_token, create_refresh_token, decode_token
from auth.services.redis import is_refresh_token_valid, store_refresh_token, revoke_refresh_token
from auth.models.user import User
import sqlalchemy as sa

router = APIRouter(tags=["auth"])

@router.post("/token/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    """トークン更新エンドポイント"""
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no_refresh_token")

    # 構造検証
    try:
        payload = decode_token(refresh_token, verify_exp=True)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token")

    # リフレッシュトークンの有効性チェック
    # 
    if not await is_refresh_token_valid(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="revoked_refresh_token")

    user_id = payload["sub"]
    token_version = payload.get("ver", 0)

    # ユーザーを取得して token_version を比較 (これは楽観的な失効なので注意)
    q = await session.execute(sa.select(User).where(User.id == user_id))
    user: User | None = q.scalar_one_or_none()
    if user is None or user.token_version != token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_revoked")

    # 新しいトークンを発行
    new_at = create_access_token(user_id)
    new_rt = create_refresh_token(user_id, user.token_version)

    # redis で回転
    await revoke_refresh_token(refresh_token)
    await store_refresh_token(new_rt)

    # クッキーを設定
    response.set_cookie(
        "refresh_token",
        new_rt,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )
    return {"access_token": new_at, "token_type": "bearer", "expires_in": 60 * 15}
