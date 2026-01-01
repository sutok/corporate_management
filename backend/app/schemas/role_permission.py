"""
RolePermission Schemas
"""
from pydantic import BaseModel, Field


class RolePermissionCreate(BaseModel):
    """ロール権限追加スキーマ"""

    permission_id: int = Field(..., description="権限ID")


class RolePermissionBatchCreate(BaseModel):
    """ロール権限一括追加スキーマ"""

    permission_ids: list[int] = Field(..., description="権限IDリスト")


class RolePermissionResponse(BaseModel):
    """ロール権限レスポンススキーマ"""

    id: int = Field(..., description="ID")
    role_id: int = Field(..., description="ロールID")
    permission_id: int = Field(..., description="権限ID")

    class Config:
        from_attributes = True
