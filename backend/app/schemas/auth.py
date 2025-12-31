"""
認証用スキーマ
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """トークンレスポンス"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """トークンペイロード"""

    user_id: Optional[int] = None
    email: Optional[str] = None
