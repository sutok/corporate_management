"""
Role Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.permission import PermissionResponse


class RoleBase(BaseModel):
    """ロール基本スキーマ"""

    code: str = Field(..., min_length=1, max_length=50, description="ロールコード（例: subscription_manager）")
    name: str = Field(..., min_length=1, max_length=255, description="ロール名")
    description: Optional[str] = Field(None, description="ロールの説明")


class RoleCreate(RoleBase):
    """ロール作成スキーマ"""

    company_id: Optional[int] = Field(None, description="企業ID（NULL=システムロール）")
    is_system: bool = Field(False, description="システムロール")


class RoleUpdate(BaseModel):
    """ロール更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="ロール名")
    description: Optional[str] = Field(None, description="ロールの説明")


class RoleResponse(RoleBase):
    """ロールレスポンススキーマ"""

    id: int = Field(..., description="ロールID")
    company_id: Optional[int] = Field(None, description="企業ID")
    is_system: bool = Field(..., description="システムロール")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True


class RoleWithPermissionsResponse(RoleResponse):
    """ロール詳細レスポンススキーマ（権限付き）"""

    permissions: List[PermissionResponse] = Field(default_factory=list, description="権限リスト")

    class Config:
        from_attributes = True
