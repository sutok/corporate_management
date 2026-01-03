"""
pytest設定とフィクスチャ
"""
import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import select

from app.main import app
from app.database import Base, get_db
from app.config import get_settings
from app.models.role import Role
from app.models.group_role import GroupRole
from app.models.group_role_permission import GroupRolePermission
from app.models.user_group_assignment import UserGroupAssignment

settings = get_settings()

# テスト用データベースURL（既存のDBを使用）
TEST_DATABASE_URL = settings.DATABASE_URL_ASYNC

# テスト用エンジン
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

# テスト用セッションメーカー
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def seed_test_permissions(session: AsyncSession):
    """テスト用の権限データを投入"""
    # 基本的な権限を作成（admin groupに全権限を与えるため）
    permissions = [
        {"code": "user.view", "name": "ユーザー閲覧", "resource_type": "user"},
        {"code": "user.create", "name": "ユーザー作成", "resource_type": "user"},
        {"code": "user.update", "name": "ユーザー更新", "resource_type": "user"},
        {"code": "user.delete", "name": "ユーザー削除", "resource_type": "user"},
        {"code": "branch.view", "name": "支店閲覧", "resource_type": "branch"},
        {"code": "branch.create", "name": "支店作成", "resource_type": "branch"},
        {"code": "branch.update", "name": "支店更新", "resource_type": "branch"},
        {"code": "branch.delete", "name": "支店削除", "resource_type": "branch"},
        {"code": "department.view", "name": "部署閲覧", "resource_type": "department"},
        {"code": "department.create", "name": "部署作成", "resource_type": "department"},
        {"code": "department.update", "name": "部署更新", "resource_type": "department"},
        {"code": "department.delete", "name": "部署削除", "resource_type": "department"},
        {"code": "company.view", "name": "企業閲覧", "resource_type": "company"},
        {"code": "company.create", "name": "企業作成", "resource_type": "company"},
        {"code": "company.update", "name": "企業更新", "resource_type": "company"},
        {"code": "company.delete", "name": "企業削除", "resource_type": "company"},
        {"code": "customer.view", "name": "顧客閲覧", "resource_type": "customer"},
        {"code": "customer.create", "name": "顧客作成", "resource_type": "customer"},
        {"code": "customer.update", "name": "顧客更新", "resource_type": "customer"},
        {"code": "customer.delete", "name": "顧客削除", "resource_type": "customer"},
        {"code": "report.view_all", "name": "全日報閲覧", "resource_type": "report"},
        {"code": "report.view_self", "name": "自分の日報閲覧", "resource_type": "report"},
        {"code": "report.create", "name": "日報作成", "resource_type": "report"},
        {"code": "report.update", "name": "日報更新", "resource_type": "report"},
        {"code": "report.update_self", "name": "自分の日報更新", "resource_type": "report"},
        {"code": "report.delete", "name": "日報削除", "resource_type": "report"},
        {"code": "report.delete_self", "name": "自分の日報削除", "resource_type": "report"},
    ]

    role_objects = []
    for perm in permissions:
        role = Role(**perm)
        session.add(role)
        role_objects.append(role)
    await session.flush()

    # adminグループを作成
    admin_group = GroupRole(
        code="test_admin",
        name="テスト管理者",
        description="テスト用の管理者グループ",
        is_system=True,
    )
    session.add(admin_group)
    await session.flush()

    # adminグループに全権限を付与
    for role in role_objects:
        group_perm = GroupRolePermission(
            group_role_id=admin_group.id,
            role_id=role.id,
        )
        session.add(group_perm)

    await session.commit()
    return admin_group.id


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """テスト用データベースセッション"""
    # テーブル作成
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # セッション提供
    async with TestSessionLocal() as session:
        # 権限データを投入
        admin_group_id = await seed_test_permissions(session)

        # セッションに admin_group_id を保存（テストで使用できるように）
        session.info["admin_group_id"] = admin_group_id

        yield session

    # クリーンアップ
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def assign_admin_permissions(session: AsyncSession, user_id: int):
    """テストユーザーに管理者権限を付与"""
    from datetime import datetime, timezone

    admin_group_id = session.info.get("admin_group_id")
    if not admin_group_id:
        # admin_group_idがない場合は、GroupRoleから取得
        result = await session.execute(select(GroupRole).where(GroupRole.code == "test_admin"))
        admin_group = result.scalar_one_or_none()
        if admin_group:
            admin_group_id = admin_group.id

    if admin_group_id:
        assignment = UserGroupAssignment(
            user_id=user_id,
            group_role_id=admin_group_id,
            assigned_by=user_id,  # 自己割り当て
            assigned_at=datetime.now(timezone.utc),
        )
        session.add(assignment)
        await session.commit()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """テスト用HTTPクライアント"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # ヘルパー関数をクライアントに追加
        ac.assign_admin_permissions = lambda user_id: assign_admin_permissions(db_session, user_id)
        yield ac

    app.dependency_overrides.clear()
