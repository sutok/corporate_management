"""
UserRole Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.role import RoleResponse


class UserRoleCreate(BaseModel):
    """ユーザーロール追加スキーマ"""

    role_id: int = Field(..., description="ロールID")


class UserRoleBatchCreate(BaseModel):
    """ユーザーロール一括追加スキーマ"""

    role_ids: list[int] = Field(..., description="ロールIDリスト")


class UserRoleResponse(BaseModel):
    """ユーザーロールレスポンススキーマ"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="ユーザーID")
    role_id: int = Field(..., description="ロールID")
    assigned_at: datetime = Field(..., description="割り当て日時")
    assigned_by: Optional[int] = Field(None, description="割り当て実行者ID")

    class Config:
        from_attributes = True


class UserRoleWithDetailsResponse(UserRoleResponse):
    """ユーザーロール詳細レスポンススキーマ（ロール情報付き）"""

    role: RoleResponse = Field(..., description="ロール情報")

    class Config:
        from_attributes = True
