"""
Company Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """企業ベーススキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="企業名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")


class CompanyCreate(CompanyBase):
    """企業作成スキーマ"""

    pass


class CompanyUpdate(BaseModel):
    """企業更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="企業名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")


class CompanyResponse(CompanyBase):
    """企業レスポンススキーマ"""

    id: int = Field(..., description="企業ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
