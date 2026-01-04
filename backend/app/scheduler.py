"""
Background scheduler for automated tasks
APSchedulerによるバックグラウンドジョブ管理
"""
import logging
from datetime import date, datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.service import CompanyServiceSubscription, ServiceSubscriptionHistory

logger = logging.getLogger(__name__)

# システム管理者ID（自動処理用）
SYSTEM_ADMIN_ID = 1


async def auto_renew_subscriptions():
    """
    サブスクリプション自動更新ジョブ

    翌日期限切れになるアクティブな契約の期限日を30日延長する
    毎日実行
    """
    logger.info("自動更新ジョブ開始")

    async with AsyncSessionLocal() as db:
        try:
            # 翌日期限切れになるアクティブな契約を取得
            tomorrow = date.today() + timedelta(days=1)

            result = await db.execute(
                select(CompanyServiceSubscription).where(
                    CompanyServiceSubscription.status == "active",
                    CompanyServiceSubscription.expired_date == tomorrow
                )
            )
            expiring_subscriptions = result.scalars().all()

            renewed_count = 0
            for subscription in expiring_subscriptions:
                old_expired_date = subscription.expired_date
                subscription.expired_date += timedelta(days=30)

                # 履歴記録
                history = ServiceSubscriptionHistory(
                    company_id=subscription.company_id,
                    subscription_id=subscription.id,
                    changed_by_user_id=SYSTEM_ADMIN_ID,
                    change_type="update",
                    old_status="active",
                    new_status="active",
                    old_end_date=old_expired_date,
                    new_end_date=subscription.expired_date,
                    old_monthly_price=subscription.monthly_price,
                    new_monthly_price=subscription.monthly_price,
                    change_reason="自動更新",
                    changed_at=datetime.now(),
                )
                db.add(history)
                renewed_count += 1

            await db.commit()
            logger.info(f"自動更新完了: {renewed_count}件の契約を更新しました")

        except Exception as e:
            logger.error(f"自動更新ジョブでエラーが発生しました: {e}")
            await db.rollback()
            raise


async def expire_cancelled_subscriptions():
    """
    期限切れ処理ジョブ

    期限日を過ぎた解約済み契約を期限切れ状態に変更する
    毎日実行
    """
    logger.info("期限切れ処理ジョブ開始")

    async with AsyncSessionLocal() as db:
        try:
            # 期限切れになった解約済み契約を取得
            today = date.today()

            result = await db.execute(
                select(CompanyServiceSubscription).where(
                    CompanyServiceSubscription.status == "cancelled",
                    CompanyServiceSubscription.expired_date < today
                )
            )
            expired_subscriptions = result.scalars().all()

            expired_count = 0
            for subscription in expired_subscriptions:
                old_status = subscription.status
                subscription.status = "expired"

                # 履歴記録
                history = ServiceSubscriptionHistory(
                    company_id=subscription.company_id,
                    subscription_id=subscription.id,
                    changed_by_user_id=SYSTEM_ADMIN_ID,
                    change_type="update",
                    old_status=old_status,
                    new_status="expired",
                    old_end_date=subscription.expired_date,
                    new_end_date=subscription.expired_date,
                    old_monthly_price=subscription.monthly_price,
                    new_monthly_price=subscription.monthly_price,
                    change_reason="期限切れ",
                    changed_at=datetime.now(),
                )
                db.add(history)
                expired_count += 1

            await db.commit()
            logger.info(f"期限切れ処理完了: {expired_count}件の契約を期限切れにしました")

        except Exception as e:
            logger.error(f"期限切れ処理ジョブでエラーが発生しました: {e}")
            await db.rollback()
            raise


def start_scheduler():
    """
    スケジューラーを起動
    """
    scheduler = AsyncIOScheduler()

    # 自動更新ジョブ: 毎日 23:00 に実行（翌日期限切れをチェック）
    scheduler.add_job(
        auto_renew_subscriptions,
        CronTrigger(hour=23, minute=0),
        id="auto_renew_subscriptions",
        name="サブスクリプション自動更新",
        replace_existing=True,
    )
    logger.info("自動更新ジョブを登録しました（毎日 23:00）")

    # 期限切れ処理ジョブ: 毎日 00:00 に実行
    scheduler.add_job(
        expire_cancelled_subscriptions,
        CronTrigger(hour=0, minute=0),
        id="expire_cancelled_subscriptions",
        name="期限切れ処理",
        replace_existing=True,
    )
    logger.info("期限切れ処理ジョブを登録しました（毎日 00:00）")

    scheduler.start()
    logger.info("スケジューラーを起動しました")

    return scheduler
