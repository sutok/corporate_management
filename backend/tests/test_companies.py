"""
Companies CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_companies_list(client: AsyncClient, db_session: AsyncSession):
    """企業一覧取得テスト"""
    # テストユーザー作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    db_session.add(user)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業一覧取得
    response = await client.get(
        "/api/companies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 1
    assert companies[0]["name"] == "テスト株式会社"


@pytest.mark.asyncio
async def test_get_company_by_id(client: AsyncClient, db_session: AsyncSession):
    """企業詳細取得テスト"""
    company = Company(name="詳細テスト株式会社", address="東京都渋谷区1-2-3")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="detail@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    db_session.add(user)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "detail@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業詳細取得
    response = await client.get(
        f"/api/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "詳細テスト株式会社"
    assert data["address"] == "東京都渋谷区1-2-3"


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient, db_session: AsyncSession):
    """企業作成テスト（管理者のみ）"""
    company = Company(name="既存企業")
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

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業作成
    response = await client.post(
        "/api/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "新規企業株式会社",
            "address": "大阪府大阪市1-2-3",
            "phone": "06-1234-5678",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "新規企業株式会社"
    assert data["address"] == "大阪府大阪市1-2-3"
    assert data["phone"] == "06-1234-5678"


@pytest.mark.asyncio
async def test_update_company(client: AsyncClient, db_session: AsyncSession):
    """企業更新テスト"""
    company = Company(name="更新前企業")
    db_session.add(company)
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

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "manager@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業更新
    response = await client.put(
        f"/api/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "更新後企業株式会社"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新後企業株式会社"


@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient, db_session: AsyncSession):
    """企業削除テスト"""
    company = Company(name="削除対象企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="delete@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "delete@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業削除
    response = await client.delete(
        f"/api/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_company_forbidden_for_regular_user(
    client: AsyncClient, db_session: AsyncSession
):
    """一般ユーザーは企業作成不可"""
    company = Company(name="既存企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="一般ユーザー",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 企業作成試行（失敗すべき）
    response = await client.post(
        "/api/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "新規企業"},
    )

    assert response.status_code == 403
    # 権限システムの新しいエラーメッセージ形式
    assert "権限" in response.json()["detail"]


# ========================================
# 権限テスト (Permission Tests)
# ========================================

@pytest.mark.asyncio
async def test_get_company_without_authentication(client: AsyncClient):
    """認証なしで企業一覧取得 - 401エラー"""
    response = await client.get("/api/companies")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_company_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで企業一覧取得 - 403エラー"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="一般ユーザー",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/companies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_post_company_without_authentication(client: AsyncClient):
    """認証なしで企業作成 - 401エラー"""
    response = await client.post("/api/companies",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_post_company_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで企業作成 - 403エラー"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="一般ユーザー",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_put_company_without_authentication(client: AsyncClient):
    """認証なしで企業更新 - 401エラー"""
    response = await client.put("/api/companies/1",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_put_company_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで企業更新 - 403エラー"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="一般ユーザー",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/companies/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_company_without_authentication(client: AsyncClient):
    """認証なしで企業削除 - 401エラー"""
    response = await client.delete("/api/companies/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_company_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで企業削除 - 403エラー"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="一般ユーザー",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await client.delete(
        "/api/companies/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]
