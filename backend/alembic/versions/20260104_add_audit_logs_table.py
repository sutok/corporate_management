"""add_audit_logs_table

Revision ID: 20260104_audit_logs
Revises: 04d602d0a423
Create Date: 2026-01-04 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260104_audit_logs'
down_revision: Union[str, None] = '04d602d0a423'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """操作履歴テーブルを作成"""
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False, comment='操作履歴ID'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='操作ユーザーID（未認証の場合はNULL）'),
        sa.Column('company_id', sa.Integer(), nullable=True, comment='企業ID（ユーザーに紐づく場合）'),
        sa.Column('method', sa.String(length=10), nullable=False, comment='HTTPメソッド'),
        sa.Column('path', sa.String(length=500), nullable=False, comment='リクエストパス'),
        sa.Column('query_params', sa.Text(), nullable=True, comment='クエリパラメータ（JSON）'),
        sa.Column('request_body', sa.Text(), nullable=True, comment='リクエストボディ（JSON、機密情報は除外）'),
        sa.Column('status_code', sa.Integer(), nullable=False, comment='レスポンスステータスコード'),
        sa.Column('response_time_ms', sa.Integer(), nullable=True, comment='レスポンス時間（ミリ秒）'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='クライアントIPアドレス'),
        sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User-Agent'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # インデックス作成
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    op.create_index('idx_audit_logs_user_id_created_at', 'audit_logs', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_audit_logs_company_id_created_at', 'audit_logs', ['company_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_company_id'), 'audit_logs', ['company_id'], unique=False)


def downgrade() -> None:
    """操作履歴テーブルを削除"""
    op.drop_index(op.f('ix_audit_logs_company_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_index('idx_audit_logs_company_id_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')
