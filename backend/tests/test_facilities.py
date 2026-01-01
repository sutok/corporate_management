"""
Facilities CRUD API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.facility import Facility
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_get_facilities_list(client: AsyncClient, db_session: AsyncSession):
    """施設一覧取得テスト"""
    company = Company(name="テスト株式会社")
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
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="東京本社",
        address="東京都渋谷区",
        phone="03-1234-5678",
    )
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設一覧取得
    response = await client.get(
        "/api/facilities",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    facilities = response.json()
    assert len(facilities) >= 1
    assert facilities[0]["name"] == "東京本社"


@pytest.mark.asyncio
async def test_get_facility_detail(client: AsyncClient, db_session: AsyncSession):
    """施設詳細取得テスト"""
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
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="大阪支社",
        address="大阪府大阪市",
    )
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設詳細取得
    response = await client.get(
        f"/api/facilities/{facility.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "大阪支社"
    assert data["address"] == "大阪府大阪市"


@pytest.mark.asyncio
async def test_create_facility(client: AsyncClient, db_session: AsyncSession):
    """施設作成テスト（管理者）"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    admin_user = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
    )
    db_session.add(admin_user)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設作成
    response = await client.post(
        "/api/facilities",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "name": "名古屋支社",
            "address": "愛知県名古屋市",
            "phone": "052-1234-5678",
            "description": "中部地区の拠点",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "名古屋支社"
    assert data["company_id"] == company.id


@pytest.mark.asyncio
async def test_create_facility_forbidden_for_regular_user(
    client: AsyncClient, db_session: AsyncSession
):
    """一般ユーザーは施設作成不可"""
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

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設作成試行（失敗すべき）
    response = await client.post(
        "/api/facilities",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "name": "福岡支社",
        },
    )

    assert response.status_code == 403
    assert "権限がありません" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_facility(client: AsyncClient, db_session: AsyncSession):
    """施設更新テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    db_session.add(user)
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="札幌支社",
        address="北海道札幌市",
    )
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設更新
    response = await client.put(
        f"/api/facilities/{facility.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "札幌営業所",
            "phone": "011-1234-5678",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "札幌営業所"
    assert data["phone"] == "011-1234-5678"


@pytest.mark.asyncio
async def test_delete_facility(client: AsyncClient, db_session: AsyncSession):
    """施設削除テスト"""
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
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="仙台支社",
    )
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設削除
    response = await client.delete(
        f"/api/facilities/{facility.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
