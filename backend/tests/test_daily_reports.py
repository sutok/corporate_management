"""
DailyReports CRUD API Tests
"""
import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.daily_report import DailyReport
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_daily_reports_list(client: AsyncClient, db_session: AsyncSession):
    """日報一覧取得テスト"""
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="営業担当",
        email="sales@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.flush()

    report = DailyReport(
        company_id=company.id,
        user_id=user.id,
        report_date=date.today(),
    )
    db_session.add(report)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 日報一覧取得
    response = await client.get(
        "/api/daily-reports",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    reports = response.json()
    assert len(reports) >= 1


@pytest.mark.asyncio
async def test_create_daily_report(client: AsyncClient, db_session: AsyncSession):
    """日報作成テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="営業担当",
        email="sales@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 日報作成
    response = await client.post(
        "/api/daily-reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": user.id,
            "report_date": str(date.today()),
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_update_daily_report(client: AsyncClient, db_session: AsyncSession):
    """日報更新テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="営業担当",
        email="sales@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.flush()

    report = DailyReport(
        company_id=company.id,
        user_id=user.id,
        report_date=date.today(),
    )
    db_session.add(report)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 日報更新
    from datetime import timedelta

    new_date = date.today() + timedelta(days=1)
    response = await client.put(
        f"/api/daily-reports/{report.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"report_date": str(new_date)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["report_date"] == str(new_date)


@pytest.mark.asyncio
async def test_delete_daily_report(client: AsyncClient, db_session: AsyncSession):
    """日報削除テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="営業担当",
        email="sales@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.flush()

    report = DailyReport(
        company_id=company.id,
        user_id=user.id,
        report_date=date.today(),
    )
    db_session.add(report)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 日報削除
    response = await client.delete(
        f"/api/daily-reports/{report.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_daily_reports_with_date_filter(
    client: AsyncClient, db_session: AsyncSession
):
    """日報一覧取得（日付フィルタ付き）"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="営業担当",
        email="sales@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.flush()

    today_report = DailyReport(company_id=company.id, user_id=user.id, report_date=date.today())
    db_session.add(today_report)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 日付フィルタ付きで日報取得
    response = await client.get(
        f"/api/daily-reports?start_date={date.today()}&end_date={date.today()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    reports = response.json()
    assert len(reports) >= 1
