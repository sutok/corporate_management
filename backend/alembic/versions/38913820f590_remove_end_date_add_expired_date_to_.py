"""remove_end_date_add_expired_date_to_subscriptions

Revision ID: 38913820f590
Revises: 83d5a8eaffc6
Create Date: 2026-01-04 22:41:56.849496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38913820f590'
down_revision: Union[str, None] = '83d5a8eaffc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. expired_dateカラムを追加（一時的にNULL許可）
    op.add_column('company_service_subscriptions',
        sa.Column('expired_date', sa.Date(), nullable=True))

    # 2. 既存データのexpired_dateを設定（start_date + 30日）
    op.execute("""
        UPDATE company_service_subscriptions
        SET expired_date = start_date + INTERVAL '30 days'
        WHERE expired_date IS NULL
    """)

    # 3. expired_dateをNOT NULLに変更
    op.alter_column('company_service_subscriptions', 'expired_date',
                    existing_type=sa.Date(),
                    nullable=False)

    # 4. end_dateカラムを削除
    op.drop_column('company_service_subscriptions', 'end_date')


def downgrade() -> None:
    # 1. end_dateカラムを追加
    op.add_column('company_service_subscriptions',
        sa.Column('end_date', sa.Date(), nullable=True))

    # 2. cancelled/expiredステータスの場合、expired_dateをend_dateにコピー
    op.execute("""
        UPDATE company_service_subscriptions
        SET end_date = expired_date
        WHERE status IN ('cancelled', 'expired')
    """)

    # 3. expired_dateカラムを削除
    op.drop_column('company_service_subscriptions', 'expired_date')
