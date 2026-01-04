"""
Users CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_users_list(client: AsyncClient, db_session: AsyncSession):
    """ユーザー一覧取得テスト（同じ企業のみ）"""
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    user1 = User(
        company_id=company.id,
        name="ユーザー1",
        email="user1@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    user2 = User(
        company_id=company.id,
        name="ユーザー2",
        email="user2@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add_all([user1, user2])
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user1.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user1@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # ユーザー一覧取得
    response = await client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    """ユーザー作成テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    admin = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(admin)
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(admin.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # ユーザー作成
    response = await client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "name": "新規ユーザー",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "user",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "新規ユーザー"
    assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session: AsyncSession):
    """ユーザー更新テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="更新前ユーザー",
        email="update@example.com",
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
        json={"email": "update@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 自分自身を更新
    response = await client.put(
        f"/api/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "更新後ユーザー"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新後ユーザー"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, db_session: AsyncSession):
    """ユーザー削除テスト（管理者のみ）"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    admin = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    target_user = User(
        company_id=company.id,
        name="削除対象ユーザー",
        email="target@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add_all([admin, target_user])
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(admin.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # ユーザー削除
    response = await client.delete(
        f"/api/users/{target_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email(
    client: AsyncClient, db_session: AsyncSession
):
    """重複メールアドレスでユーザー作成失敗"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    existing_user = User(
        company_id=company.id,
        name="既存ユーザー",
        email="existing@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    admin = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add_all([existing_user, admin])
    await db_session.commit()

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(admin.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 重複メールでユーザー作成試行
    response = await client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "name": "新規ユーザー",
            "email": "existing@example.com",
            "password": "password123",
            "role": "user",
        },
    )

    assert response.status_code == 400
    assert "既に使用されています" in response.json()["detail"]


# ========================================
# 権限テスト (Permission Tests)
# ========================================

@pytest.mark.asyncio
async def test_get_user_without_authentication(client: AsyncClient):
    """認証なしでユーザー一覧取得 - 401エラー"""
    response = await client.get("/api/users")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_user_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしでユーザー一覧取得 - 403エラー"""
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
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_post_user_without_authentication(client: AsyncClient):
    """認証なしでユーザー作成 - 401エラー"""
    response = await client.post("/api/users",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_post_user_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしでユーザー作成 - 403エラー"""
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
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_put_user_without_authentication(client: AsyncClient):
    """認証なしでユーザー更新 - 401エラー"""
    response = await client.put("/api/users/1",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_put_user_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしでユーザー更新 - 403エラー"""
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
        "/api/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_user_without_authentication(client: AsyncClient):
    """認証なしでユーザー削除 - 401エラー"""
    response = await client.delete("/api/users/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_user_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしでユーザー削除 - 403エラー"""
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
        "/api/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]
