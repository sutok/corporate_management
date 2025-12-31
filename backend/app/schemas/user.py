"""
ユーザー用スキーマ
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """ユーザー基本情報"""

    name: str
    email: EmailStr
    role: str
    position: Optional[str] = None


class UserCreate(UserBase):
    """ユーザー作成"""

    company_id: int
    password: str


class UserUpdate(BaseModel):
    """ユーザー更新"""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    position: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """ユーザーレスポンス"""

    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
