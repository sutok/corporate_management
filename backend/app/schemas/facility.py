"""
Facility Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FacilityBase(BaseModel):
    """施設基本スキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="施設名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    description: Optional[str] = Field(None, description="説明")


class FacilityCreate(FacilityBase):
    """施設作成スキーマ"""

    company_id: int = Field(..., description="所属企業ID")


class FacilityUpdate(BaseModel):
    """施設更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="施設名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    description: Optional[str] = Field(None, description="説明")


class FacilityResponse(FacilityBase):
    """施設レスポンススキーマ"""

    id: int = Field(..., description="施設ID")
    company_id: int = Field(..., description="所属企業ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
