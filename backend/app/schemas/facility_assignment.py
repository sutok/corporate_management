"""
FacilityAssignment Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FacilityAssignmentBase(BaseModel):
    """施設所属基本スキーマ"""

    contract_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="契約形態（正社員、契約社員、派遣、業務委託など）",
    )


class FacilityAssignmentCreate(FacilityAssignmentBase):
    """施設所属作成スキーマ"""

    company_id: int = Field(..., description="企業ID")
    facility_id: int = Field(..., description="施設ID")
    user_id: int = Field(..., description="ユーザーID")


class FacilityAssignmentUpdate(BaseModel):
    """施設所属更新スキーマ"""

    contract_type: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="契約形態（正社員、契約社員、派遣、業務委託など）",
    )


class FacilityAssignmentResponse(FacilityAssignmentBase):
    """施設所属レスポンススキーマ"""

    id: int = Field(..., description="所属ID")
    company_id: int = Field(..., description="企業ID")
    facility_id: int = Field(..., description="施設ID")
    user_id: int = Field(..., description="ユーザーID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True
