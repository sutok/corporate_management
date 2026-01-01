"""
Service Subscription API テスト
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.service import Service, CompanyServiceSubscription, ServiceSubscriptionHistory
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.auth.password import get_password_hash


async def create_test_data(db_session: AsyncSession):
    """テストデータ作成ヘルパー"""
    # 企業作成
    company = Company(
        name="テスト株式会社",
        address="東京都渋谷区1-2-3",
        phone="03-1234-5678",
    )
    db_session.add(company)
    await db_session.flush()

    # 権限作成
    perm_view = Permission(
        code="subscription.view",
        name="契約状況閲覧",
        description="自社の契約状況を閲覧する",
        resource_type="subscription",
    )
    perm_history = Permission(
        code="subscription.history",
        name="契約履歴閲覧",
        description="契約履歴を閲覧する",
        resource_type="subscription",
    )
    perm_subscribe = Permission(
        code="service.subscribe",
        name="サービス契約",
        description="サービスを契約する",
        resource_type="service",
    )
    db_session.add_all([perm_view, perm_history, perm_subscribe])
    await db_session.flush()

    # ロール作成
    role_manager = Role(
        company_id=company.id,
        code="subscription_manager",
        name="サービス管理者",
        description="サービス契約の管理を行う",
        is_system=False,
    )
    db_session.add(role_manager)
    await db_session.flush()

    # ロールに権限を割り当て
    db_session.add_all([
        RolePermission(role_id=role_manager.id, permission_id=perm_view.id),
        RolePermission(role_id=role_manager.id, permission_id=perm_history.id),
        RolePermission(role_id=role_manager.id, permission_id=perm_subscribe.id),
    ])

    # ユーザー作成
    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
        position="マネージャー",
    )
    db_session.add(user)
    await db_session.flush()

    # ユーザーにロールを割り当て
    user_role = UserRole(
        user_id=user.id,
        role_id=role_manager.id,
        assigned_by=user.id,
    )
    db_session.add(user_role)

    # サービス作成
    service = Service(
        service_code="basic_plan",
        service_name="ベーシックプラン",
        description="基本的なサービス",
        base_price=10000.00,
        is_active=True,
    )
    db_session.add(service)
    await db_session.flush()

    # 契約作成
    subscription = CompanyServiceSubscription(
        company_id=company.id,
        service_id=service.id,
        status="active",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        monthly_price=10000.00,
    )
    db_session.add(subscription)
    await db_session.commit()

    return {
        "company": company,
        "user": user,
        "role": role_manager,
        "service": service,
        "subscription": subscription,
        "permissions": {
            "view": perm_view,
            "history": perm_history,
            "subscribe": perm_subscribe,
        }
    }


async def get_auth_token(client: AsyncClient) -> str:
    """認証トークン取得ヘルパー"""
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_subscriptions_success(client: AsyncClient, db_session: AsyncSession):
    """契約一覧取得成功テスト"""
    # テストデータ作成
    await create_test_data(db_session)

    # 認証トークン取得
    token = await get_auth_token(client)

    # 契約一覧取得
    response = await client.get(
        "/api/subscriptions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "active"
    assert data[0]["monthly_price"] == 10000.0


@pytest.mark.asyncio
async def test_get_subscriptions_unauthorized(client: AsyncClient, db_session: AsyncSession):
    """契約一覧取得 - 認証なしでエラー"""
    await create_test_data(db_session)

    # 認証トークンなしでアクセス
    response = await client.get("/api/subscriptions")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_subscriptions_without_permission(client: AsyncClient, db_session: AsyncSession):
    """契約一覧取得 - 権限なしでエラー"""
    # 権限のないユーザーでテスト
    company = Company(name="テスト株式会社2")
    db_session.add(company)
    await db_session.flush()

    user_no_perm = User(
        company_id=company.id,
        name="権限なしユーザー",
        email="noperm@example.com",
        password_hash=get_password_hash("password123"),
        role="staff",
    )
    db_session.add(user_no_perm)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "noperm@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 契約一覧取得試行
    response = await client.get(
        "/api/subscriptions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限が不足しています" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_subscription_history_success(client: AsyncClient, db_session: AsyncSession):
    """契約履歴取得成功テスト"""
    test_data = await create_test_data(db_session)
    token = await get_auth_token(client)

    # 履歴レコード作成
    history1 = ServiceSubscriptionHistory(
        subscription_id=test_data["subscription"].id,
        changed_by_user_id=test_data["user"].id,
        change_type="create",
        new_status="active",
        new_monthly_price=10000.00,
        change_reason="初回契約",
        changed_at=datetime.now(),
    )
    history2 = ServiceSubscriptionHistory(
        subscription_id=test_data["subscription"].id,
        changed_by_user_id=test_data["user"].id,
        change_type="update",
        old_status="active",
        new_status="active",
        old_monthly_price=10000.00,
        new_monthly_price=12000.00,
        change_reason="価格改定",
        changed_at=datetime.now() + timedelta(days=1),
    )
    db_session.add_all([history1, history2])
    await db_session.commit()

    # 契約履歴取得
    response = await client.get(
        "/api/subscriptions/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # 新しい順にソートされているか確認
    assert data[0]["change_type"] == "update"
    assert data[0]["new_monthly_price"] == 12000.00
    assert data[1]["change_type"] == "create"
    assert data[1]["new_monthly_price"] == 10000.00


@pytest.mark.asyncio
async def test_get_subscription_history_with_filter(client: AsyncClient, db_session: AsyncSession):
    """契約履歴取得 - subscription_id フィルタ"""
    test_data = await create_test_data(db_session)
    token = await get_auth_token(client)

    # 履歴レコード作成
    history = ServiceSubscriptionHistory(
        subscription_id=test_data["subscription"].id,
        changed_by_user_id=test_data["user"].id,
        change_type="create",
        new_status="active",
        new_monthly_price=10000.00,
        change_reason="初回契約",
        changed_at=datetime.now(),
    )
    db_session.add(history)
    await db_session.commit()

    # 特定の契約の履歴取得
    response = await client.get(
        f"/api/subscriptions/history?subscription_id={test_data['subscription'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["subscription_id"] == test_data["subscription"].id


@pytest.mark.asyncio
async def test_get_subscription_history_forbidden(client: AsyncClient, db_session: AsyncSession):
    """契約履歴取得 - 他社の契約履歴はアクセス不可"""
    test_data = await create_test_data(db_session)

    # 他社の企業とサービス契約を作成
    other_company = Company(name="他社")
    db_session.add(other_company)
    await db_session.flush()

    other_subscription = CompanyServiceSubscription(
        company_id=other_company.id,
        service_id=test_data["service"].id,
        status="active",
        start_date=date.today(),
        monthly_price=10000.00,
    )
    db_session.add(other_subscription)
    await db_session.commit()

    token = await get_auth_token(client)

    # 他社の契約履歴にアクセス試行
    response = await client.get(
        f"/api/subscriptions/history?subscription_id={other_subscription.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "他社の契約履歴は閲覧できません" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_subscription_history_empty(client: AsyncClient, db_session: AsyncSession):
    """契約履歴取得 - 履歴が存在しない場合"""
    await create_test_data(db_session)
    token = await get_auth_token(client)

    # 履歴レコードを作成せずに取得
    response = await client.get(
        "/api/subscriptions/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_services_success(client: AsyncClient, db_session: AsyncSession):
    """サービス一覧取得成功テスト"""
    await create_test_data(db_session)
    token = await get_auth_token(client)

    # サービス一覧取得（認証必要）
    response = await client.get(
        "/api/subscriptions/services",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["service_code"] == "basic_plan"
