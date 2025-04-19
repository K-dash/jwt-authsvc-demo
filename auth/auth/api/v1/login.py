from __future__ import annotations

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.user import User
from auth.schemas.auth import LoginRequest, Token
from auth.services.db import get_session
from auth.services.jwt import create_access_token, create_refresh_token
from auth.services.redis import store_refresh_token

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=Token)
async def login(data: LoginRequest, resp: Response, session: AsyncSession = Depends(get_session)) -> Token:
    """ログインエンドポイント"""
    q = await session.execute(sa.select(User).where(User.email == data.email))
    user: User | None = q.scalar_one_or_none()
    if user is None or not pwd_context.verify(data.password, user.pw_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id), user.token_version)

    await store_refresh_token(refresh_token)

    resp.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )
    return Token(access_token=access_token, expires_in=60 * 15)
