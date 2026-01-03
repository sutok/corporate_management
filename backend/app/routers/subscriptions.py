"""
Service Subscription API
サービス契約管理API（権限チェックの実装例）
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.service import CompanyServiceSubscription, Service, ServiceSubscriptionHistory
from app.auth.permissions import require_permission, require_any_permission

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_subscriptions(
    current_user: User = Depends(require_permission("subscription.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    契約一覧取得

    必要な権限: subscription.view
    """
    query = select(CompanyServiceSubscription).where(
        CompanyServiceSubscription.company_id == current_user.company_id
    )
    result = await db.execute(query)
    subscriptions = result.scalars().all()

    return [
        {
            "id": sub.id,
            "service_id": sub.service_id,
            "status": sub.status,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "monthly_price": float(sub.monthly_price),
        }
        for sub in subscriptions
    ]


@router.get("/history", status_code=status.HTTP_200_OK)
async def get_subscription_history(
    subscription_id: int = None,
    current_user: User = Depends(require_permission("subscription.history")),
    db: AsyncSession = Depends(get_db),
):
    """
    契約履歴取得

    必要な権限: subscription.history

    Parameters:
    - subscription_id: 特定の契約の履歴のみ取得（オプション）
    """
    # 履歴クエリ構築（company_idで直接フィルタリング）
    query = select(ServiceSubscriptionHistory).where(
        ServiceSubscriptionHistory.company_id == current_user.company_id
    )

    # 特定の契約IDが指定された場合
    if subscription_id is not None:
        # 自社の契約かチェック（company_idで確認）
        subscription_check = await db.execute(
            select(CompanyServiceSubscription.id).where(
                CompanyServiceSubscription.id == subscription_id,
                CompanyServiceSubscription.company_id == current_user.company_id
            )
        )
        if subscription_check.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="他社の契約履歴は閲覧できません"
            )
        query = query.where(ServiceSubscriptionHistory.subscription_id == subscription_id)

    # 履歴を新しい順に取得
    query = query.order_by(ServiceSubscriptionHistory.changed_at.desc())
    result = await db.execute(query)
    history_records = result.scalars().all()

    return [
        {
            "id": record.id,
            "company_id": record.company_id,
            "subscription_id": record.subscription_id,
            "change_type": record.change_type,
            "old_status": record.old_status,
            "new_status": record.new_status,
            "old_end_date": record.old_end_date,
            "new_end_date": record.new_end_date,
            "old_monthly_price": float(record.old_monthly_price) if record.old_monthly_price else None,
            "new_monthly_price": float(record.new_monthly_price) if record.new_monthly_price else None,
            "change_reason": record.change_reason,
            "changed_by_user_id": record.changed_by_user_id,
            "changed_at": record.changed_at,
        }
        for record in history_records
    ]


@router.post("/{service_id}/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_service(
    service_id: int,
    current_user: User = Depends(require_permission("service.subscribe")),
    db: AsyncSession = Depends(get_db),
):
    """
    サービス契約

    必要な権限: service.subscribe
    """
    # サービスの存在確認
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="サービスが見つかりません"
        )

    if not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このサービスは現在提供されていません"
        )

    # 既存の契約確認
    existing_result = await db.execute(
        select(CompanyServiceSubscription).where(
            CompanyServiceSubscription.company_id == current_user.company_id,
            CompanyServiceSubscription.service_id == service_id,
            CompanyServiceSubscription.status == "active"
        )
    )
    existing_sub = existing_result.scalar_one_or_none()

    if existing_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="既にこのサービスを契約しています"
        )

    # 新規契約作成
    from datetime import date
    new_subscription = CompanyServiceSubscription(
        company_id=current_user.company_id,
        service_id=service_id,
        status="active",
        start_date=date.today(),
        monthly_price=service.base_price,
    )

    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)

    return {
        "id": new_subscription.id,
        "service_id": new_subscription.service_id,
        "status": new_subscription.status,
        "start_date": new_subscription.start_date,
        "monthly_price": float(new_subscription.monthly_price),
        "message": "サービスの契約が完了しました"
    }


@router.post("/{subscription_id}/unsubscribe", status_code=status.HTTP_200_OK)
async def unsubscribe_service(
    subscription_id: int,
    current_user: User = Depends(require_permission("service.unsubscribe")),
    db: AsyncSession = Depends(get_db),
):
    """
    サービス解約

    必要な権限: service.unsubscribe
    """
    # 契約の存在確認
    sub_result = await db.execute(
        select(CompanyServiceSubscription).where(
            CompanyServiceSubscription.id == subscription_id
        )
    )
    subscription = sub_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="契約が見つかりません"
        )

    # 自社の契約のみ解約可能
    if subscription.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他社の契約は解約できません"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この契約は既に解約されています"
        )

    # 契約を解約に変更
    from datetime import date
    subscription.status = "cancelled"
    subscription.end_date = date.today()

    await db.commit()
    await db.refresh(subscription)

    return {
        "id": subscription.id,
        "status": subscription.status,
        "end_date": subscription.end_date,
        "message": "サービスの解約が完了しました"
    }


@router.get("/services", status_code=status.HTTP_200_OK)
async def get_available_services(
    current_user: User = Depends(require_any_permission(["service.view", "subscription.view"])),
    db: AsyncSession = Depends(get_db),
):
    """
    利用可能なサービス一覧取得

    必要な権限: service.view または subscription.view（いずれか）
    """
    query = select(Service).where(Service.is_active == True)
    result = await db.execute(query)
    services = result.scalars().all()

    return [
        {
            "id": service.id,
            "service_code": service.service_code,
            "service_name": service.service_name,
            "description": service.description,
            "base_price": float(service.base_price),
        }
        for service in services
    ]
