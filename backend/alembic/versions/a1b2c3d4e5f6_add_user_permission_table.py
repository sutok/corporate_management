"""add_user_permission_table

Revision ID: a1b2c3d4e5f6
Revises: 4903fe892a89
Create Date: 2026-01-02 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '4903fe892a89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_permissions テーブル作成
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ユーザーID'),
        sa.Column('permission_id', sa.Integer(), nullable=False, comment='権限ID'),
        sa.Column('granted_by', sa.Integer(), nullable=True, comment='付与者ID（監査用）'),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='付与日時'),
        sa.Column('reason', sa.Text(), nullable=True, comment='付与理由（任意）'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'permission_id', name='uq_user_permission')
    )

    # インデックス作成
    op.create_index(op.f('ix_user_permissions_id'), 'user_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_user_permissions_user_id'), 'user_permissions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_permissions_permission_id'), 'user_permissions', ['permission_id'], unique=False)


def downgrade() -> None:
    # インデックス削除
    op.drop_index(op.f('ix_user_permissions_permission_id'), table_name='user_permissions')
    op.drop_index(op.f('ix_user_permissions_user_id'), table_name='user_permissions')
    op.drop_index(op.f('ix_user_permissions_id'), table_name='user_permissions')

    # テーブル削除
    op.drop_table('user_permissions')
