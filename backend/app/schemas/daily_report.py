"""
DailyReport Schemas
"""
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class DailyReportBase(BaseModel):
    """日報ベーススキーマ"""

    report_date: date = Field(..., description="報告日")


class DailyReportCreate(DailyReportBase):
    """日報作成スキーマ"""

    user_id: int = Field(..., description="作成者ID")


class DailyReportUpdate(BaseModel):
    """日報更新スキーマ"""

    report_date: date = Field(None, description="報告日")


class DailyReportResponse(DailyReportBase):
    """日報レスポンススキーマ"""

    id: int = Field(..., description="日報ID")
    user_id: int = Field(..., description="作成者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)
