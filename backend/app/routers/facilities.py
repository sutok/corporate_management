"""
Facility CRUD API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityUpdate, FacilityResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("", response_model=List[FacilityResponse])
async def get_facilities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設一覧取得（自社のみ）"""
    result = await db.execute(
        select(Facility).where(Facility.company_id == current_user.company_id)
    )
    facilities = result.scalars().all()
    return facilities


@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    facility_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設詳細取得"""
    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設が見つかりません",
        )

    # 自社の施設のみアクセス可能
    if facility.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設にアクセスする権限がありません",
        )

    return facility


@router.post("", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
async def create_facility(
    facility: FacilityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設作成（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    # 自社の施設のみ作成可能
    if facility.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他社の施設は作成できません",
        )

    new_facility = Facility(**facility.model_dump())
    db.add(new_facility)
    await db.commit()
    await db.refresh(new_facility)
    return new_facility


@router.put("/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    facility_id: int,
    facility_update: FacilityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設更新（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設が見つかりません",
        )

    # 自社の施設のみ更新可能
    if facility.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設を更新する権限がありません",
        )

    # 更新
    update_data = facility_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(facility, key, value)

    await db.commit()
    await db.refresh(facility)
    return facility


@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility(
    facility_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設削除（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設が見つかりません",
        )

    # 自社の施設のみ削除可能
    if facility.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設を削除する権限がありません",
        )

    await db.delete(facility)
    await db.commit()
