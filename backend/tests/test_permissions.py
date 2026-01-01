"""
権限管理機能テスト
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.auth.password import get_password_hash
from app.auth.permissions import get_user_permissions


@pytest.mark.asyncio
async def test_create_permission(db_session: AsyncSession):
    """Permission作成テスト"""
    permission = Permission(
        code="test.view",
        name="テスト閲覧",
        description="テスト用の権限",
        resource_type="test",
    )
    db_session.add(permission)
    await db_session.commit()

    assert permission.id is not None
    assert permission.code == "test.view"
    assert permission.resource_type == "test"


@pytest.mark.asyncio
async def test_create_role(db_session: AsyncSession):
    """Role作成テスト"""
    # 企業作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    # ロール作成
    role = Role(
        company_id=company.id,
        code="test_role",
        name="テストロール",
        description="テスト用のロール",
        is_system=False,
    )
    db_session.add(role)
    await db_session.commit()

    assert role.id is not None
    assert role.code == "test_role"
    assert role.company_id == company.id
    assert role.is_system is False


@pytest.mark.asyncio
async def test_create_system_role(db_session: AsyncSession):
    """システムロール作成テスト"""
    role = Role(
        company_id=None,
        code="system_admin",
        name="システム管理者",
        description="システムロール",
        is_system=True,
    )
    db_session.add(role)
    await db_session.commit()

    assert role.id is not None
    assert role.company_id is None
    assert role.is_system is True


@pytest.mark.asyncio
async def test_role_permission_assignment(db_session: AsyncSession):
    """ロールへの権限割り当てテスト"""
    # 権限作成
    permission1 = Permission(
        code="user.view",
        name="ユーザー閲覧",
        resource_type="user",
    )
    permission2 = Permission(
        code="user.create",
        name="ユーザー作成",
        resource_type="user",
    )
    db_session.add_all([permission1, permission2])
    await db_session.flush()

    # ロール作成
    role = Role(
        company_id=None,
        code="user_manager",
        name="ユーザー管理者",
        is_system=True,
    )
    db_session.add(role)
    await db_session.flush()

    # ロールに権限を割り当て
    role_perm1 = RolePermission(role_id=role.id, permission_id=permission1.id)
    role_perm2 = RolePermission(role_id=role.id, permission_id=permission2.id)
    db_session.add_all([role_perm1, role_perm2])
    await db_session.commit()

    assert role_perm1.id is not None
    assert role_perm2.id is not None


@pytest.mark.asyncio
async def test_user_role_assignment(db_session: AsyncSession):
    """ユーザーへのロール割り当てテスト"""
    # 企業作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    # ユーザー作成
    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="staff",
    )
    db_session.add(user)
    await db_session.flush()

    # ロール作成
    role = Role(
        company_id=company.id,
        code="editor",
        name="編集者",
        is_system=False,
    )
    db_session.add(role)
    await db_session.flush()

    # ユーザーにロールを割り当て
    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
        assigned_by=user.id,
    )
    db_session.add(user_role)
    await db_session.commit()

    assert user_role.id is not None
    assert user_role.user_id == user.id
    assert user_role.role_id == role.id


@pytest.mark.asyncio
async def test_get_user_permissions(db_session: AsyncSession):
    """ユーザーの権限取得テスト"""
    # 企業作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    # 権限作成
    perm_view = Permission(code="report.view", name="レポート閲覧", resource_type="report")
    perm_create = Permission(code="report.create", name="レポート作成", resource_type="report")
    db_session.add_all([perm_view, perm_create])
    await db_session.flush()

    # ロール作成
    role = Role(
        company_id=company.id,
        code="reporter",
        name="レポーター",
        is_system=False,
    )
    db_session.add(role)
    await db_session.flush()

    # ロールに権限を割り当て
    db_session.add_all([
        RolePermission(role_id=role.id, permission_id=perm_view.id),
        RolePermission(role_id=role.id, permission_id=perm_create.id),
    ])

    # ユーザー作成
    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="staff",
    )
    db_session.add(user)
    await db_session.flush()

    # ユーザーにロールを割り当て
    user_role = UserRole(user_id=user.id, role_id=role.id, assigned_by=user.id)
    db_session.add(user_role)
    await db_session.commit()

    # ユーザーの権限を取得
    permissions = await get_user_permissions(db_session, user.id)

    assert len(permissions) == 2
    assert "report.view" in permissions
    assert "report.create" in permissions


@pytest.mark.asyncio
async def test_user_multiple_roles(db_session: AsyncSession):
    """ユーザーの複数ロール割り当てテスト"""
    # 企業作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    # 権限作成
    perm1 = Permission(code="service.view", name="サービス閲覧", resource_type="service")
    perm2 = Permission(code="user.view", name="ユーザー閲覧", resource_type="user")
    perm3 = Permission(code="user.create", name="ユーザー作成", resource_type="user")
    db_session.add_all([perm1, perm2, perm3])
    await db_session.flush()

    # ロール1: サービス管理者
    role1 = Role(company_id=company.id, code="service_admin", name="サービス管理者", is_system=False)
    db_session.add(role1)
    await db_session.flush()
    db_session.add(RolePermission(role_id=role1.id, permission_id=perm1.id))

    # ロール2: ユーザー管理者
    role2 = Role(company_id=company.id, code="user_admin", name="ユーザー管理者", is_system=False)
    db_session.add(role2)
    await db_session.flush()
    db_session.add_all([
        RolePermission(role_id=role2.id, permission_id=perm2.id),
        RolePermission(role_id=role2.id, permission_id=perm3.id),
    ])

    # ユーザー作成
    user = User(
        company_id=company.id,
        name="マルチロールユーザー",
        email="multi@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()

    # ユーザーに両方のロールを割り当て
    db_session.add_all([
        UserRole(user_id=user.id, role_id=role1.id, assigned_by=user.id),
        UserRole(user_id=user.id, role_id=role2.id, assigned_by=user.id),
    ])
    await db_session.commit()

    # ユーザーの権限を取得
    permissions = await get_user_permissions(db_session, user.id)

    assert len(permissions) == 3
    assert "service.view" in permissions
    assert "user.view" in permissions
    assert "user.create" in permissions
