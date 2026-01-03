"""
User API Router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.auth.permissions import require_permission, require_any_permission, check_permission
from app.auth.password import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("user.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー一覧取得

    必要な権限: user.view
    """
    result = await db.execute(
        select(User)
        .where(User.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー詳細取得

    必要な権限: user.view
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_permission("user.create")),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー作成

    必要な権限: user.create
    """
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他の企業のユーザーは作成できません",
        )

    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に使用されています",
        )

    user_data = user.model_dump()
    password = user_data.pop("password")
    user_data["password_hash"] = get_password_hash(password)

    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_any_permission(["user.update", "user.update_self"])),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー更新

    必要な権限: user.update (他人も更新可能) OR user.update_self (自分のみ)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    # 自分以外を更新する場合は user.update 権限が必要
    if user.id != current_user.id:
        has_update_permission = await check_permission(db, current_user.id, "user.update")
        if not has_update_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="他のユーザーを更新する権限がありません",
            )

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user.delete")),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー削除

    必要な権限: user.delete
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    await db.delete(user)
    await db.commit()
