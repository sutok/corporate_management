"""add_permission_management_system

Revision ID: 83d5a8eaffc6
Revises: 04d602d0a423
Create Date: 2026-01-03 11:46:14.633864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83d5a8eaffc6'
down_revision: Union[str, None] = '04d602d0a423'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. roles テーブル作成（個別権限一覧）
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False, comment='権限ID'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='権限コード（例: user.create）'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='権限名'),
        sa.Column('description', sa.Text(), nullable=True, comment='権限の説明'),
        sa.Column('resource_type', sa.String(length=50), nullable=False, comment='リソース種別（例: user）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新日時'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_roles_code'),
        comment='個別権限一覧'
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_resource_type'), 'roles', ['resource_type'], unique=False)

    # 2. group_roles テーブル作成（グループ一覧）
    op.create_table(
        'group_roles',
        sa.Column('id', sa.Integer(), nullable=False, comment='グループID'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='グループコード（例: admin）'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='グループ名'),
        sa.Column('description', sa.Text(), nullable=True, comment='グループの説明'),
        sa.Column('company_id', sa.Integer(), nullable=True, comment='企業ID（NULLの場合はシステムグループ）'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false', comment='システムグループか'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新日時'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_group_roles_code'),
        comment='グループ一覧'
    )
    op.create_index(op.f('ix_group_roles_id'), 'group_roles', ['id'], unique=False)
    op.create_index(op.f('ix_group_roles_company_id'), 'group_roles', ['company_id'], unique=False)

    # 3. group_role_permissions テーブル作成（グループに含まれる権限）
    op.create_table(
        'group_role_permissions',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
        sa.Column('group_role_id', sa.Integer(), nullable=False, comment='グループID'),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='権限ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['group_role_id'], ['group_roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_role_id', 'role_id', name='uq_group_role_permissions'),
        comment='グループに含まれる権限（グループ⇔権限）'
    )
    op.create_index(op.f('ix_group_role_permissions_id'), 'group_role_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_group_role_permissions_group_role_id'), 'group_role_permissions', ['group_role_id'], unique=False)
    op.create_index(op.f('ix_group_role_permissions_role_id'), 'group_role_permissions', ['role_id'], unique=False)

    # 4. user_role_assignments テーブル作成（ユーザーへの個別権限割り当て）
    op.create_table(
        'user_role_assignments',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ユーザーID'),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='権限ID'),
        sa.Column('granted_by', sa.Integer(), nullable=True, comment='付与者ID'),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False, comment='付与日時'),
        sa.Column('reason', sa.Text(), nullable=True, comment='付与理由（監査用）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role_assignments'),
        comment='ユーザーへの個別権限割り当て（ユーザー⇔権限）'
    )
    op.create_index(op.f('ix_user_role_assignments_id'), 'user_role_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_user_role_assignments_user_id'), 'user_role_assignments', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_role_assignments_role_id'), 'user_role_assignments', ['role_id'], unique=False)

    # 5. user_group_assignments テーブル作成（ユーザーのグループ所属）
    op.create_table(
        'user_group_assignments',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ユーザーID'),
        sa.Column('group_role_id', sa.Integer(), nullable=False, comment='グループID'),
        sa.Column('assigned_by', sa.Integer(), nullable=True, comment='割り当てた人'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, comment='割り当て日時'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['group_role_id'], ['group_roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'group_role_id', name='uq_user_group_assignments'),
        comment='ユーザーのグループ所属（ユーザー⇔グループ）'
    )
    op.create_index(op.f('ix_user_group_assignments_id'), 'user_group_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_user_group_assignments_user_id'), 'user_group_assignments', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_group_assignments_group_role_id'), 'user_group_assignments', ['group_role_id'], unique=False)


def downgrade() -> None:
    # テーブル削除（外部キー制約のある順に削除）
    op.drop_index(op.f('ix_user_group_assignments_group_role_id'), table_name='user_group_assignments')
    op.drop_index(op.f('ix_user_group_assignments_user_id'), table_name='user_group_assignments')
    op.drop_index(op.f('ix_user_group_assignments_id'), table_name='user_group_assignments')
    op.drop_table('user_group_assignments')

    op.drop_index(op.f('ix_user_role_assignments_role_id'), table_name='user_role_assignments')
    op.drop_index(op.f('ix_user_role_assignments_user_id'), table_name='user_role_assignments')
    op.drop_index(op.f('ix_user_role_assignments_id'), table_name='user_role_assignments')
    op.drop_table('user_role_assignments')

    op.drop_index(op.f('ix_group_role_permissions_role_id'), table_name='group_role_permissions')
    op.drop_index(op.f('ix_group_role_permissions_group_role_id'), table_name='group_role_permissions')
    op.drop_index(op.f('ix_group_role_permissions_id'), table_name='group_role_permissions')
    op.drop_table('group_role_permissions')

    op.drop_index(op.f('ix_group_roles_company_id'), table_name='group_roles')
    op.drop_index(op.f('ix_group_roles_id'), table_name='group_roles')
    op.drop_table('group_roles')

    op.drop_index(op.f('ix_roles_resource_type'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
