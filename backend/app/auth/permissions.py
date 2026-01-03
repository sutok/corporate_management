"""
Permission Management System
権限管理システム - Linux風の個別権限＋グループ権限モデル
"""
from typing import Set
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, union
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.user_role_assignment import UserRoleAssignment
from app.models.group_role_permission import GroupRolePermission
from app.models.user_group_assignment import UserGroupAssignment


async def get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
    """
    ユーザーの最終権限を取得

    最終権限 = 個別権限 ∪ グループ権限 (UNION)

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        Set[str]: 権限コードのセット（例: {"user.create", "report.view"}）
    """
    # 1. 個別権限を取得（直接付与された権限）
    direct_query = (
        select(Role.code)
        .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
        .where(UserRoleAssignment.user_id == user_id)
    )

    # 2. グループ権限を取得（グループ経由で取得した権限）
    group_query = (
        select(Role.code)
        .join(GroupRolePermission, GroupRolePermission.role_id == Role.id)
        .join(UserGroupAssignment, UserGroupAssignment.group_role_id == GroupRolePermission.group_role_id)
        .where(UserGroupAssignment.user_id == user_id)
    )

    # 3. UNION で統合（重複は自動的に除外される）
    combined_query = union(direct_query, group_query)
    result = await db.execute(combined_query)
    permissions = result.scalars().all()

    return set(permissions)


async def check_permission(db: AsyncSession, user_id: int, required_permission: str) -> bool:
    """
    ユーザーが特定の権限を持っているかチェック

    Args:
        db: データベースセッション
        user_id: ユーザーID
        required_permission: 必要な権限コード（例: "user.create"）

    Returns:
        bool: 権限があればTrue、なければFalse
    """
    user_permissions = await get_user_permissions(db, user_id)
    return required_permission in user_permissions


async def check_permissions(db: AsyncSession, user_id: int, required_permissions: list[str]) -> bool:
    """
    ユーザーが複数の権限を全て持っているかチェック

    Args:
        db: データベースセッション
        user_id: ユーザーID
        required_permissions: 必要な権限コードのリスト

    Returns:
        bool: 全ての権限があればTrue、一つでも欠けていればFalse
    """
    user_permissions = await get_user_permissions(db, user_id)
    return all(perm in user_permissions for perm in required_permissions)


async def check_any_permission(db: AsyncSession, user_id: int, required_permissions: list[str]) -> bool:
    """
    ユーザーが複数の権限のいずれかを持っているかチェック

    Args:
        db: データベースセッション
        user_id: ユーザーID
        required_permissions: 必要な権限コードのリスト

    Returns:
        bool: いずれかの権限があればTrue、全て無ければFalse
    """
    user_permissions = await get_user_permissions(db, user_id)
    return any(perm in user_permissions for perm in required_permissions)


def require_permission(required_permission: str):
    """
    権限チェック用のDependency（単一権限）

    使い方:
        @router.post("/users")
        async def create_user(
            current_user: User = Depends(require_permission("user.create"))
        ):
            ...

    Args:
        required_permission: 必要な権限コード

    Returns:
        Dependency: FastAPI Dependency関数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # ユーザーの権限を取得
        has_permission = await check_permission(db, current_user.id, required_permission)

        # 権限チェック
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"権限が不足しています: {required_permission}",
            )

        return current_user

    return permission_checker


def require_permissions(required_permissions: list[str]):
    """
    権限チェック用のDependency（複数権限 - 全て必要）

    使い方:
        @router.post("/admin/users")
        async def admin_create_user(
            current_user: User = Depends(require_permissions(["user.create", "admin.access"]))
        ):
            ...

    Args:
        required_permissions: 必要な権限コードのリスト（全て必要）

    Returns:
        Dependency: FastAPI Dependency関数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # ユーザーの権限を取得
        has_all_permissions = await check_permissions(db, current_user.id, required_permissions)

        # 権限チェック
        if not has_all_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"必要な権限が不足しています: {', '.join(required_permissions)}",
            )

        return current_user

    return permission_checker


def require_any_permission(required_permissions: list[str]):
    """
    権限チェック用のDependency（複数権限 - いずれか一つ）

    使い方:
        @router.get("/reports")
        async def view_reports(
            current_user: User = Depends(require_any_permission(["report.view", "report.admin"]))
        ):
            ...

    Args:
        required_permissions: 必要な権限コードのリスト（いずれか一つ）

    Returns:
        Dependency: FastAPI Dependency関数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # ユーザーの権限を取得
        has_any_permission = await check_any_permission(db, current_user.id, required_permissions)

        # 権限チェック
        if not has_any_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"以下のいずれかの権限が必要です: {', '.join(required_permissions)}",
            )

        return current_user

    return permission_checker
