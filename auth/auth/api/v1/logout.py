from __future__ import annotations

from fastapi import APIRouter, Cookie, Response
from auth.services.redis import revoke_refresh_token

router = APIRouter(tags=["auth"])

@router.post("/logout", status_code=200)
async def logout(response: Response, refresh_token: str | None = Cookie(default=None)):
    """ログアウトエンドポイント"""
    if refresh_token:
        await revoke_refresh_token(refresh_token)
    response.delete_cookie("refresh_token", path="/")
    return {"detail": "logged_out"}
