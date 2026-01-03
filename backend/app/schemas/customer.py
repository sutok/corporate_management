"""
Customer Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    """顧客ベーススキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="顧客名")
    company_name: Optional[str] = Field(None, max_length=255, description="会社名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    notes: Optional[str] = Field(None, description="備考")


class CustomerCreate(CustomerBase):
    """顧客作成スキーマ"""

    company_id: int = Field(..., description="所属企業ID")
    assigned_user_id: Optional[int] = Field(None, description="担当営業ID")


class CustomerUpdate(BaseModel):
    """顧客更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="顧客名")
    company_name: Optional[str] = Field(None, max_length=255, description="会社名")
    address: Optional[str] = Field(None, max_length=500, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    notes: Optional[str] = Field(None, description="備考")
    assigned_user_id: Optional[int] = Field(None, description="担当営業ID")


class CustomerResponse(CustomerBase):
    """顧客レスポンススキーマ"""

    id: int = Field(..., description="顧客ID")
    company_id: int = Field(..., description="所属企業ID")
    assigned_user_id: Optional[int] = Field(None, description="担当営業ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)
