"""
認証APIテスト
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """ログイン成功テスト"""
    # テストデータ作成
    company = Company(
        name="テスト株式会社",
        address="東京都渋谷区1-2-3",
        phone="03-1234-5678",
    )
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
        position="マネージャー",
    )
    db_session.add(user)
    await db_session.commit()

    # ログインテスト
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient, db_session: AsyncSession):
    """存在しないメールアドレスでログイン失敗"""
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert "正しくありません" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session: AsyncSession):
    """間違ったパスワードでログイン失敗"""
    # テストデータ作成
    company = Company(
        name="テスト株式会社",
        address="東京都渋谷区1-2-3",
    )
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

    # 間違ったパスワードでログイン
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, db_session: AsyncSession):
    """/me エンドポイント成功テスト"""
    # テストデータ作成
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
        position="マネージャー",
    )
    db_session.add(user)
    await db_session.commit()

    # ログインしてトークン取得
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # /me エンドポイントにアクセス
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "テストユーザー"
    assert data["role"] == "manager"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """トークンなしで/meにアクセス → 401エラー"""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """無効なトークンで/meにアクセス → 401エラー"""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
