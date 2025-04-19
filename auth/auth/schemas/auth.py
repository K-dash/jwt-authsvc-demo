from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRead(BaseModel):
    """ユーザーリストレスポンス"""
    id: UUID
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """トークンレスポンス"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Seconds until the access token expires")
