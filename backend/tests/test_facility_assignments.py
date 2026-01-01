"""
FacilityAssignment API Tests
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.models.facility import Facility
from app.models.facility_assignment import FacilityAssignment
from app.auth.password import get_password_hash


@pytest.mark.asyncio
async def test_create_facility_assignment(client: AsyncClient, db_session: AsyncSession):
    """施設所属作成テスト"""
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
    await db_session.flush()

    employee = User(
        company_id=company.id,
        name="社員",
        email="employee@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(employee)
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="東京本社",
    )
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設所属作成
    response = await client.post(
        "/api/facility-assignments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "facility_id": facility.id,
            "user_id": employee.id,
            "contract_type": "正社員",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["facility_id"] == facility.id
    assert data["user_id"] == employee.id
    assert data["contract_type"] == "正社員"


@pytest.mark.asyncio
async def test_create_duplicate_assignment_fails(
    client: AsyncClient, db_session: AsyncSession
):
    """重複した施設所属作成は失敗する"""
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
    await db_session.flush()

    employee = User(
        company_id=company.id,
        name="社員",
        email="employee@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(employee)
    await db_session.flush()

    facility = Facility(
        company_id=company.id,
        name="大阪支社",
    )
    db_session.add(facility)
    await db_session.flush()

    # 既存の所属を作成
    assignment = FacilityAssignment(
        company_id=company.id,
        facility_id=facility.id,
        user_id=employee.id,
        contract_type="正社員",
    )
    db_session.add(assignment)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 重複した施設所属作成試行（失敗すべき）
    response = await client.post(
        "/api/facility-assignments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "facility_id": facility.id,
            "user_id": employee.id,
            "contract_type": "契約社員",
        },
    )

    assert response.status_code == 400
    assert "既に" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_facility_assignments_by_user(
    client: AsyncClient, db_session: AsyncSession
):
    """ユーザーの施設所属一覧取得テスト"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        name="社員",
        email="employee@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add(user)
    await db_session.flush()

    facility1 = Facility(company_id=company.id, name="東京本社")
    facility2 = Facility(company_id=company.id, name="大阪支社")
    db_session.add_all([facility1, facility2])
    await db_session.flush()

    assignment1 = FacilityAssignment(
        company_id=company.id,
        facility_id=facility1.id,
        user_id=user.id,
        contract_type="正社員",
    )
    assignment2 = FacilityAssignment(
        company_id=company.id,
        facility_id=facility2.id,
        user_id=user.id,
        contract_type="出向",
    )
    db_session.add_all([assignment1, assignment2])
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "employee@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # ユーザーの施設所属一覧取得
    response = await client.get(
        f"/api/facility-assignments?user_id={user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assignments = response.json()
    assert len(assignments) == 2


@pytest.mark.asyncio
async def test_get_facility_assignments_by_facility(
    client: AsyncClient, db_session: AsyncSession
):
    """施設の所属ユーザー一覧取得テスト"""
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
    user1 = User(
        company_id=company.id,
        name="社員1",
        email="user1@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    user2 = User(
        company_id=company.id,
        name="社員2",
        email="user2@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add_all([admin, user1, user2])
    await db_session.flush()

    facility = Facility(company_id=company.id, name="名古屋支社")
    db_session.add(facility)
    await db_session.flush()

    assignment1 = FacilityAssignment(
        company_id=company.id,
        facility_id=facility.id,
        user_id=user1.id,
        contract_type="正社員",
    )
    assignment2 = FacilityAssignment(
        company_id=company.id,
        facility_id=facility.id,
        user_id=user2.id,
        contract_type="派遣",
    )
    db_session.add_all([assignment1, assignment2])
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設の所属ユーザー一覧取得
    response = await client.get(
        f"/api/facility-assignments?facility_id={facility.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assignments = response.json()
    assert len(assignments) == 2


@pytest.mark.asyncio
async def test_update_facility_assignment(
    client: AsyncClient, db_session: AsyncSession
):
    """施設所属更新テスト（契約形態変更）"""
    company = Company(name="テスト企業")
    db_session.add(company)
    await db_session.flush()

    admin = User(
        company_id=company.id,
        name="管理者",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="manager",
    )
    employee = User(
        company_id=company.id,
        name="社員",
        email="employee@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add_all([admin, employee])
    await db_session.flush()

    facility = Facility(company_id=company.id, name="福岡支社")
    db_session.add(facility)
    await db_session.flush()

    assignment = FacilityAssignment(
        company_id=company.id,
        facility_id=facility.id,
        user_id=employee.id,
        contract_type="契約社員",
    )
    db_session.add(assignment)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 契約形態を更新
    response = await client.put(
        f"/api/facility-assignments/{assignment.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"contract_type": "正社員"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contract_type"] == "正社員"


@pytest.mark.asyncio
async def test_delete_facility_assignment(
    client: AsyncClient, db_session: AsyncSession
):
    """施設所属削除テスト"""
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
    employee = User(
        company_id=company.id,
        name="社員",
        email="employee@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
    )
    db_session.add_all([admin, employee])
    await db_session.flush()

    facility = Facility(company_id=company.id, name="仙台支社")
    db_session.add(facility)
    await db_session.flush()

    assignment = FacilityAssignment(
        company_id=company.id,
        facility_id=facility.id,
        user_id=employee.id,
        contract_type="派遣",
    )
    db_session.add(assignment)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設所属削除
    response = await client.delete(
        f"/api/facility-assignments/{assignment.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_assignment_forbidden_for_regular_user(
    client: AsyncClient, db_session: AsyncSession
):
    """一般ユーザーは施設所属作成不可"""
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
    await db_session.flush()

    facility = Facility(company_id=company.id, name="広島支社")
    db_session.add(facility)
    await db_session.commit()

    # ログイン
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # 施設所属作成試行（失敗すべき）
    response = await client.post(
        "/api/facility-assignments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company.id,
            "facility_id": facility.id,
            "user_id": user.id,
            "contract_type": "正社員",
        },
    )

    assert response.status_code == 403
    assert "権限がありません" in response.json()["detail"]
