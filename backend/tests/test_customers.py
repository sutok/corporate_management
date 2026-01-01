"""
Customers CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.customer import Customer
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_customers_list(client: AsyncClient, db_session: AsyncSession):
    """顧客一覧取得テスト"""
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

    customer = Customer(
        company_id=company.id,
        assigned_user_id=user.id,
        name="顧客A",
        company_name="A株式会社",
    )
    db_session.add(customer)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 顧客一覧取得
    response = await client.get(
        "/api/customers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    customers = response.json()
    assert len(customers) >= 1
    assert customers[0]["name"] == "顧客A"


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient, db_session: AsyncSession):
    """顧客作成テスト"""
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

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 顧客作成
    response = await client.post(
        "/api/customers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "assigned_user_id": user.id,
            "name": "新規顧客",
            "company_name": "新規株式会社",
            "email": "customer@example.com",
            "phone": "03-1234-5678",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "新規顧客"
    assert data["company_name"] == "新規株式会社"


@pytest.mark.asyncio
async def test_update_customer(client: AsyncClient, db_session: AsyncSession):
    """顧客更新テスト"""
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

    customer = Customer(
        company_id=company.id,
        name="更新前顧客",
    )
    db_session.add(customer)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 顧客更新
    response = await client.put(
        f"/api/customers/{customer.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "更新後顧客", "assigned_user_id": user.id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新後顧客"


@pytest.mark.asyncio
async def test_delete_customer(client: AsyncClient, db_session: AsyncSession):
    """顧客削除テスト"""
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

    customer = Customer(
        company_id=company.id,
        name="削除対象顧客",
    )
    db_session.add(customer)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "sales@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 顧客削除
    response = await client.delete(
        f"/api/customers/{customer.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
