"""
Department Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    """部署ベーススキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="部署名")
    description: Optional[str] = Field(None, description="説明")


class DepartmentCreate(DepartmentBase):
    """部署作成スキーマ"""

    branch_id: int = Field(..., description="所属支店ID")


class DepartmentUpdate(BaseModel):
    """部署更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="部署名")
    description: Optional[str] = Field(None, description="説明")


class DepartmentResponse(DepartmentBase):
    """部署レスポンススキーマ"""

    id: int = Field(..., description="部署ID")
    branch_id: int = Field(..., description="所属支店ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
