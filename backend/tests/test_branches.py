"""
Branches CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.branch import Branch
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_branches_list(client: AsyncClient, db_session: AsyncSession):
    """支店一覧取得テスト"""
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(
        company_id=company.id,
        name="東京本社",
        address="東京都渋谷区1-2-3",
    )
    db_session.add(branch)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="manager@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    db_session.add(user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "manager@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 支店一覧取得
    response = await client.get(
        "/api/branches",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    branches = response.json()
    assert len(branches) >= 1
    assert branches[0]["name"] == "東京本社"


@pytest.mark.asyncio
async def test_create_branch(client: AsyncClient, db_session: AsyncSession):
    """支店作成テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 支店作成
    response = await client.post(
        "/api/branches",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "name": "大阪支社",
            "address": "大阪府大阪市1-2-3",
            "phone": "06-1234-5678",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "大阪支社"
    assert data["address"] == "大阪府大阪市1-2-3"


@pytest.mark.asyncio
async def test_update_branch(client: AsyncClient, db_session: AsyncSession):
    """支店更新テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(
        company_id=company.id,
        name="更新前支店",
    )
    db_session.add(branch)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="manager@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    db_session.add(user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "manager@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 支店更新
    response = await client.put(
        f"/api/branches/{branch.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "更新後支店"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新後支店"


@pytest.mark.asyncio
async def test_delete_branch(client: AsyncClient, db_session: AsyncSession):
    """支店削除テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(
        company_id=company.id,
        name="削除対象支店",
    )
    db_session.add(branch)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 支店削除
    response = await client.delete(
        f"/api/branches/{branch.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
