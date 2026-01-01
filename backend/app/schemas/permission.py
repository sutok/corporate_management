"""
Permission Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """権限基本スキーマ"""

    code: str = Field(..., min_length=1, max_length=100, description="権限コード（例: service.subscribe）")
    name: str = Field(..., min_length=1, max_length=255, description="権限名")
    description: Optional[str] = Field(None, description="権限の説明")
    resource_type: str = Field(..., min_length=1, max_length=50, description="リソースタイプ")


class PermissionCreate(PermissionBase):
    """権限作成スキーマ"""

    pass


class PermissionUpdate(BaseModel):
    """権限更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="権限名")
    description: Optional[str] = Field(None, description="権限の説明")
    resource_type: Optional[str] = Field(None, min_length=1, max_length=50, description="リソースタイプ")


class PermissionResponse(PermissionBase):
    """権限レスポンススキーマ"""

    id: int = Field(..., description="権限ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
