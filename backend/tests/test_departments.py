"""
Departments CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.branch import Branch
from app.models.department import Department
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_departments_list(client: AsyncClient, db_session: AsyncSession):
    """部署一覧取得テスト"""
    company = Company(name="テスト株式会社")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(company_id=company.id, name="本社")
    db_session.add(branch)
    await db_session.flush()

    department = Department(
        branch_id=branch.id,
        name="営業部",
        description="営業部門",
    )
    db_session.add(department)
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

    # 部署一覧取得
    response = await client.get(
        "/api/departments",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    departments = response.json()
    assert len(departments) >= 1
    assert departments[0]["name"] == "営業部"


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, db_session: AsyncSession):
    """部署作成テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(company_id=company.id, name="本社")
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

    # テストユーザーに管理者権限を付与
    await client.assign_admin_permissions(user.id)

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 部署作成
    response = await client.post(
        "/api/departments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "branch_id": branch.id,
            "name": "技術部",
            "description": "技術開発部門",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "技術部"
    assert data["description"] == "技術開発部門"


@pytest.mark.asyncio
async def test_update_department(client: AsyncClient, db_session: AsyncSession):
    """部署更新テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(company_id=company.id, name="本社")
    db_session.add(branch)
    await db_session.flush()

    department = Department(
        branch_id=branch.id,
        name="更新前部署",
    )
    db_session.add(department)
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

    # 部署更新
    response = await client.put(
        f"/api/departments/{department.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "更新後部署"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新後部署"


@pytest.mark.asyncio
async def test_delete_department(client: AsyncClient, db_session: AsyncSession):
    """部署削除テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    branch = Branch(company_id=company.id, name="本社")
    db_session.add(branch)
    await db_session.flush()

    department = Department(
        branch_id=branch.id,
        name="削除対象部署",
    )
    db_session.add(department)
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

    # 部署削除
    response = await client.delete(
        f"/api/departments/{department.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


# ========================================
# 権限テスト (Permission Tests)
# ========================================

@pytest.mark.asyncio
async def test_get_department_without_authentication(client: AsyncClient):
    """認証なしで部署一覧取得 - 401エラー"""
    response = await client.get("/api/departments")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_department_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで部署一覧取得 - 403エラー"""
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
        "/api/departments",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_post_department_without_authentication(client: AsyncClient):
    """認証なしで部署作成 - 401エラー"""
    response = await client.post("/api/departments",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_post_department_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで部署作成 - 403エラー"""
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
        "/api/departments",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_put_department_without_authentication(client: AsyncClient):
    """認証なしで部署更新 - 401エラー"""
    response = await client.put("/api/departments/1",
        json={"name": "テスト"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_put_department_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで部署更新 - 403エラー"""
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
        "/api/departments/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "テスト"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_department_without_authentication(client: AsyncClient):
    """認証なしで部署削除 - 401エラー"""
    response = await client.delete("/api/departments/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_department_without_permission(client: AsyncClient, db_session: AsyncSession):
    """権限なしで部署削除 - 403エラー"""
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
        "/api/departments/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "権限" in response.json()["detail"]
