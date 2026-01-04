"""
サブスクリプションチェック機能
"""
from typing import Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.service import Service, CompanyServiceSubscription


async def check_service_subscription(
    user: User,
    service_code: str,
    db: AsyncSession,
) -> bool:
    """
    ユーザーの企業が指定されたサービスを契約しているかチェック

    Args:
        user: 現在のユーザー
        service_code: サービスコード (例: "DAILY_REPORT")
        db: データベースセッション

    Returns:
        契約している場合True、していない場合False

    Raises:
        HTTPException: サービスが存在しない場合
    """
    # サービスを取得
    result = await db.execute(
        select(Service).where(Service.service_code == service_code)
    )
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サービスが見つかりません: {service_code}",
        )

    # 企業のサブスクリプションを確認
    result = await db.execute(
        select(CompanyServiceSubscription).where(
            CompanyServiceSubscription.company_id == user.company_id,
            CompanyServiceSubscription.service_id == service.id,
            CompanyServiceSubscription.status == "active",
        )
    )
    subscription = result.scalar_one_or_none()

    return subscription is not None


async def require_service_subscription(
    user: User,
    service_code: str,
    db: AsyncSession,
) -> None:
    """
    サービスの契約を必須とする（契約していない場合は403エラー）

    Args:
        user: 現在のユーザー
        service_code: サービスコード (例: "DAILY_REPORT")
        db: データベースセッション

    Raises:
        HTTPException: 契約していない場合（403 Forbidden）
    """
    has_subscription = await check_service_subscription(user, service_code, db)

    if not has_subscription:
        # サービス名を取得（エラーメッセージ用）
        result = await db.execute(
            select(Service).where(Service.service_code == service_code)
        )
        service = result.scalar_one_or_none()
        service_name = service.service_name if service else service_code

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"このサービスは契約されていません: {service_name}。企業管理者にお問い合わせください。",
        )


def require_daily_report_subscription() -> Callable:
    """
    日報サービスの契約を必須とする依存性関数

    使用例:
        @router.get("/daily-reports")
        async def get_daily_reports(
            user: User = Depends(get_current_active_user),
            _: None = Depends(require_daily_report_subscription()),
            db: AsyncSession = Depends(get_db),
        ):
            # 日報機能の処理
            pass

    Returns:
        依存性関数
    """
    async def dependency(
        user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        await require_service_subscription(user, "DAILY_REPORT", db)

    return dependency
