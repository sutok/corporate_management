"""
Branch Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BranchBase(BaseModel):
    """支店ベーススキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="支店名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")


class BranchCreate(BranchBase):
    """支店作成スキーマ"""

    company_id: int = Field(..., description="所属企業ID")


class BranchUpdate(BaseModel):
    """支店更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="支店名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")


class BranchResponse(BranchBase):
    """支店レスポンススキーマ"""

    id: int = Field(..., description="支店ID")
    company_id: int = Field(..., description="所属企業ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
