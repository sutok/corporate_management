"""
FacilityAssignment API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.models.facility import Facility
from app.models.facility_assignment import FacilityAssignment
from app.schemas.facility_assignment import (
    FacilityAssignmentCreate,
    FacilityAssignmentUpdate,
    FacilityAssignmentResponse,
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/facility-assignments", tags=["facility-assignments"])


@router.get("", response_model=List[FacilityAssignmentResponse])
async def get_facility_assignments(
    user_id: int = None,
    facility_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設所属一覧取得（自社のみ、user_idまたはfacility_idでフィルタ可能）"""
    query = select(FacilityAssignment).where(
        FacilityAssignment.company_id == current_user.company_id
    )

    if user_id is not None:
        query = query.where(FacilityAssignment.user_id == user_id)

    if facility_id is not None:
        query = query.where(FacilityAssignment.facility_id == facility_id)

    result = await db.execute(query)
    assignments = result.scalars().all()
    return assignments


@router.get("/{assignment_id}", response_model=FacilityAssignmentResponse)
async def get_facility_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設所属詳細取得"""
    result = await db.execute(
        select(FacilityAssignment).where(FacilityAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設所属が見つかりません",
        )

    # 自社のデータのみアクセス可能
    if assignment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設所属にアクセスする権限がありません",
        )

    return assignment


@router.post(
    "", response_model=FacilityAssignmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_facility_assignment(
    assignment: FacilityAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設所属作成（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    # 自社のデータのみ作成可能
    if assignment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他社の施設所属は作成できません",
        )

    # ユーザーと施設が同じ企業に所属しているか確認
    user_result = await db.execute(select(User).where(User.id == assignment.user_id))
    user = user_result.scalar_one_or_none()

    facility_result = await db.execute(
        select(Facility).where(Facility.id == assignment.facility_id)
    )
    facility = facility_result.scalar_one_or_none()

    if not user or not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーまたは施設が見つかりません",
        )

    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他社のユーザーを指定できません",
        )

    if facility.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他社の施設を指定できません",
        )

    try:
        new_assignment = FacilityAssignment(**assignment.model_dump())
        db.add(new_assignment)
        await db.commit()
        await db.refresh(new_assignment)
        return new_assignment
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザーは既にこの施設に所属しています",
        )


@router.put("/{assignment_id}", response_model=FacilityAssignmentResponse)
async def update_facility_assignment(
    assignment_id: int,
    assignment_update: FacilityAssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設所属更新（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    result = await db.execute(
        select(FacilityAssignment).where(FacilityAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設所属が見つかりません",
        )

    # 自社のデータのみ更新可能
    if assignment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設所属を更新する権限がありません",
        )

    # 更新
    update_data = assignment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)

    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """施設所属削除（管理者のみ）"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    result = await db.execute(
        select(FacilityAssignment).where(FacilityAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="施設所属が見つかりません",
        )

    # 自社のデータのみ削除可能
    if assignment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この施設所属を削除する権限がありません",
        )

    await db.delete(assignment)
    await db.commit()
