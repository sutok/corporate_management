"""
Permission System Usage Examples
権限システムの使用例
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.auth.permissions import (
    require_permission,
    require_permissions,
    require_any_permission,
    get_user_permissions,
)

router = APIRouter(prefix="/api/examples", tags=["permission-examples"])


# 例1: 単一権限チェック
@router.post("/users")
async def create_user(
    current_user: User = Depends(require_permission("user.create")),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー作成エンドポイント

    必要な権限: user.create
    """
    return {
        "message": "ユーザー作成",
        "user": current_user.name,
        "required_permission": "user.create",
    }


# 例2: 複数権限チェック（全て必要）
@router.post("/admin/users")
async def admin_create_user(
    current_user: User = Depends(require_permissions(["user.create", "admin.access"])),
    db: AsyncSession = Depends(get_db),
):
    """
    管理者用ユーザー作成エンドポイント

    必要な権限: user.create AND admin.access（両方必要）
    """
    return {
        "message": "管理者権限でユーザー作成",
        "user": current_user.name,
        "required_permissions": ["user.create", "admin.access"],
    }


# 例3: 複数権限チェック（いずれか一つ）
@router.get("/reports")
async def view_reports(
    current_user: User = Depends(require_any_permission(["report.view", "report.admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    レポート閲覧エンドポイント

    必要な権限: report.view OR report.admin（いずれか一つ）
    """
    return {
        "message": "レポート閲覧",
        "user": current_user.name,
        "required_permissions": "report.view OR report.admin",
    }


# 例4: ユーザーの全権限を取得
@router.get("/my-permissions")
async def get_my_permissions(
    current_user: User = Depends(require_permission("user.view_self")),
    db: AsyncSession = Depends(get_db),
):
    """
    現在のユーザーが持つ全権限を取得

    必要な権限: user.view_self
    """
    # ユーザーの全権限を取得
    permissions = await get_user_permissions(db, current_user.id)

    return {
        "user": current_user.name,
        "permissions": sorted(list(permissions)),
        "total": len(permissions),
    }


# 例5: カスタム権限チェック
@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(require_any_permission(["report.delete", "report.admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    レポート削除エンドポイント

    必要な権限: report.delete OR report.admin
    """
    # ビジネスロジック: レポートの所有者チェックなど
    # if report.user_id != current_user.id and not has_permission("report.admin"):
    #     raise HTTPException(403, "自分のレポートのみ削除できます")

    return {
        "message": f"レポート {report_id} を削除",
        "user": current_user.name,
        "report_id": report_id,
    }
