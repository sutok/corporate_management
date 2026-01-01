"""
Permission Check Utilities
権限チェック用のヘルパー関数と依存性注入
"""
from typing import Set, List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.auth.dependencies import get_current_user


async def get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
    """
    ユーザーの全権限を取得

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        権限コードのセット（例: {"service.subscribe", "user.view"}）
    """
    query = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
        .distinct()
    )

    result = await db.execute(query)
    permissions = result.scalars().all()

    return set(permissions)


async def check_permissions(
    user: User,
    required_permissions: List[str],
    db: AsyncSession,
    require_all: bool = True
) -> bool:
    """
    ユーザーが指定された権限を持っているかチェック

    Args:
        user: ユーザーオブジェクト
        required_permissions: 必要な権限のリスト
        db: データベースセッション
        require_all: Trueの場合すべての権限が必要、Falseの場合いずれかの権限でOK

    Returns:
        権限がある場合True、ない場合False
    """
    user_permissions = await get_user_permissions(db, user.id)

    if require_all:
        # すべての権限が必要
        return all(perm in user_permissions for perm in required_permissions)
    else:
        # いずれかの権限があればOK
        return any(perm in user_permissions for perm in required_permissions)


def require_permission(*permissions: str, require_all: bool = True):
    """
    権限チェックを行う依存性注入関数を生成

    使用例:
        @router.post("/api/services/subscribe")
        async def subscribe_service(
            current_user: User = Depends(require_permission("service.subscribe")),
            ...
        ):
            pass

    Args:
        *permissions: 必要な権限（複数指定可能）
        require_all: すべての権限が必要か（デフォルト: True）

    Returns:
        FastAPI依存性注入関数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """権限をチェックして、権限がある場合はユーザーを返す"""
        if not permissions:
            # 権限指定なしの場合は認証済みであればOK
            return current_user

        has_permission = await check_permissions(
            current_user,
            list(permissions),
            db,
            require_all=require_all
        )

        if not has_permission:
            if require_all:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"権限が不足しています。必要な権限: {', '.join(permissions)}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"権限が不足しています。必要な権限（いずれか）: {', '.join(permissions)}"
                )

        return current_user

    return permission_checker


def require_any_permission(*permissions: str):
    """
    いずれかの権限があればOKとする依存性注入関数を生成

    使用例:
        @router.get("/api/reports")
        async def get_reports(
            current_user: User = Depends(require_any_permission("report.view", "report.view_all")),
            ...
        ):
            pass

    Args:
        *permissions: 必要な権限（いずれか）

    Returns:
        FastAPI依存性注入関数
    """
    return require_permission(*permissions, require_all=False)


async def get_user_permissions_detailed(
    db: AsyncSession,
    user_id: int
) -> dict:
    """
    ユーザーの権限を詳細情報付きで取得

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        権限の詳細情報（code, name, description, resource_type）のリスト
    """
    query = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
        .distinct()
    )

    result = await db.execute(query)
    permissions = result.scalars().all()

    return {
        "user_id": user_id,
        "permissions": [
            {
                "code": perm.code,
                "name": perm.name,
                "description": perm.description,
                "resource_type": perm.resource_type,
            }
            for perm in permissions
        ]
    }
