"""
Branch API Router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.branch import Branch
from app.models.user import User
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.auth.permissions import require_permission

router = APIRouter(prefix="/api/branches", tags=["branches"])


@router.get("", response_model=List[BranchResponse])
async def get_branches(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("branch.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店一覧取得

    必要な権限: branch.view
    """
    result = await db.execute(
        select(Branch)
        .where(Branch.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    branches = result.scalars().all()
    return branches


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: int,
    current_user: User = Depends(require_permission("branch.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店詳細取得

    必要な権限: branch.view
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    return branch


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch: BranchCreate,
    current_user: User = Depends(require_permission("branch.create")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店作成

    必要な権限: branch.create
    """
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他の企業の支店は作成できません",
        )

    new_branch = Branch(**branch.model_dump())
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    return new_branch


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_update: BranchUpdate,
    current_user: User = Depends(require_permission("branch.update")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店更新

    必要な権限: branch.update
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    update_data = branch_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)

    await db.commit()
    await db.refresh(branch)
    return branch


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: int,
    current_user: User = Depends(require_permission("branch.delete")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店削除

    必要な権限: branch.delete
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    await db.delete(branch)
    await db.commit()
