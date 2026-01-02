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
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.auth.dependencies import get_current_user


async def get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
    """
    ユーザーの全権限を取得（個別権限 + ロール権限）

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        権限コードのセット（例: {"service.subscribe", "user.view"}）
    """
    from app.models.user_permission import UserPermission

    # 個別権限を取得
    direct_query = (
        select(Permission.code)
        .join(UserPermission, UserPermission.permission_id == Permission.id)
        .where(UserPermission.user_id == user_id)
    )

    # ロール権限を取得
    role_query = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
    )

    # UNION で統合
    combined_query = direct_query.union(role_query)

    result = await db.execute(combined_query)
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
    ユーザーの権限を詳細情報付きで取得（個別権限 + ロール権限）

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        権限の詳細情報（code, name, description, source, etc.）のリスト
        source: 'direct' = 個別権限, 'role' = ロール権限
    """
    from app.models.user_permission import UserPermission

    permissions_list = []

    # 個別権限を取得
    direct_query = (
        select(
            Permission.code,
            Permission.name,
            Permission.description,
            Permission.resource_type,
            UserPermission.granted_by,
            UserPermission.granted_at,
            UserPermission.reason
        )
        .join(UserPermission, UserPermission.permission_id == Permission.id)
        .where(UserPermission.user_id == user_id)
    )

    direct_result = await db.execute(direct_query)
    for row in direct_result:
        # granted_by のユーザー名を取得
        granter_name = None
        if row.granted_by:
            granter = await db.get(User, row.granted_by)
            granter_name = granter.name if granter else None

        permissions_list.append({
            "code": row.code,
            "name": row.name,
            "description": row.description,
            "resource_type": row.resource_type,
            "source": "direct",
            "granted_by": granter_name,
            "granted_at": row.granted_at.isoformat() if row.granted_at else None,
            "reason": row.reason,
        })

    # ロール権限を取得
    role_query = (
        select(
            Permission.code,
            Permission.name,
            Permission.description,
            Permission.resource_type,
            Role.name.label("role_name")
        )
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )

    role_result = await db.execute(role_query)

    # ロール権限をグループ化（同じ権限が複数のロールから来る場合）
    role_perms_dict = {}
    for row in role_result:
        if row.code not in role_perms_dict:
            role_perms_dict[row.code] = {
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "resource_type": row.resource_type,
                "source": "role",
                "via_roles": []
            }
        role_perms_dict[row.code]["via_roles"].append(row.role_name)

    # 個別権限が既にあるものは除外（個別権限が優先）
    direct_codes = {p["code"] for p in permissions_list}
    for code, perm_data in role_perms_dict.items():
        if code not in direct_codes:
            permissions_list.append(perm_data)

    return {
        "user_id": user_id,
        "permissions": permissions_list
    }
