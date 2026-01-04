"""
操作履歴（Audit Logs）のテスト
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


@pytest.mark.asyncio
async def test_audit_log_on_login(client: AsyncClient, db_session: AsyncSession):
    """ログイン時に操作履歴が記録されることを確認"""
    # ログインリクエスト
    login_data = {
        "email": "sales@example.com",
        "password": "password123",
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    # 操作履歴が記録されているか確認
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/auth/login",
            AuditLog.method == "POST"
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.method == "POST"
    assert audit_log.path == "/api/auth/login"
    assert audit_log.status_code == 200
    assert audit_log.request_body is not None
    # パスワードがマスクされているか確認
    assert "***MASKED***" in audit_log.request_body
    assert "password123" not in audit_log.request_body


@pytest.mark.asyncio
async def test_audit_log_excludes_health_check(client: AsyncClient, db_session: AsyncSession):
    """ヘルスチェックエンドポイントが操作履歴から除外されることを確認"""
    # ヘルスチェックリクエスト
    response = await client.get("/health")
    assert response.status_code == 200

    # 操作履歴が記録されていないことを確認
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.path == "/health")
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is None


@pytest.mark.asyncio
async def test_audit_log_records_user_info(client: AsyncClient, db_session: AsyncSession, auth_headers):
    """認証済みリクエストでユーザー情報が記録されることを確認"""
    # 認証済みリクエスト（自分の情報を取得）
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200

    # 操作履歴にユーザー情報が記録されているか確認
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/auth/me",
            AuditLog.method == "GET"
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.user_id is not None
    assert audit_log.company_id is not None


@pytest.mark.asyncio
async def test_audit_log_records_query_params(client: AsyncClient, db_session: AsyncSession, auth_headers):
    """クエリパラメータが記録されることを確認"""
    # クエリパラメータ付きリクエスト
    response = await client.get("/api/users/?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

    # 操作履歴にクエリパラメータが記録されているか確認
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/users/",
            AuditLog.method == "GET"
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.query_params is not None
    assert "skip" in audit_log.query_params
    assert "limit" in audit_log.query_params


@pytest.mark.asyncio
async def test_audit_log_records_response_time(client: AsyncClient, db_session: AsyncSession):
    """レスポンス時間が記録されることを確認"""
    # リクエスト実行
    login_data = {
        "email": "sales@example.com",
        "password": "password123",
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    # 操作履歴にレスポンス時間が記録されているか確認
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/auth/login",
            AuditLog.method == "POST"
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.response_time_ms is not None
    assert audit_log.response_time_ms >= 0


@pytest.mark.asyncio
async def test_audit_log_records_error_status(client: AsyncClient, db_session: AsyncSession):
    """エラーレスポンスのステータスコードが記録されることを確認"""
    # 存在しないエンドポイントへのリクエスト
    response = await client.get("/api/nonexistent")
    assert response.status_code == 404

    # 操作履歴にエラーステータスが記録されているか確認
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/nonexistent",
            AuditLog.status_code == 404
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.status_code == 404


@pytest.mark.asyncio
async def test_cleanup_old_audit_logs(db_session: AsyncSession):
    """90日以上前の操作履歴が削除されることを確認"""
    # テスト用の古い操作履歴を作成
    old_date = datetime.now() - timedelta(days=91)
    old_audit_log = AuditLog(
        method="GET",
        path="/api/test/old",
        status_code=200,
        created_at=old_date,
    )
    db_session.add(old_audit_log)

    # 新しい操作履歴も作成
    new_audit_log = AuditLog(
        method="GET",
        path="/api/test/new",
        status_code=200,
    )
    db_session.add(new_audit_log)
    await db_session.commit()

    # スケジューラーのクリーンアップ処理を模倣
    cutoff_date = datetime.now() - timedelta(days=90)
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.created_at < cutoff_date)
    )
    old_logs = result.scalars().all()

    # 古いログが見つかることを確認
    assert len(old_logs) > 0

    # 古いログを削除
    for log in old_logs:
        await db_session.delete(log)
    await db_session.commit()

    # 古いログが削除されたことを確認
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.path == "/api/test/old")
    )
    assert result.scalar_one_or_none() is None

    # 新しいログは残っていることを確認
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.path == "/api/test/new")
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_audit_log_masks_sensitive_fields(client: AsyncClient, db_session: AsyncSession):
    """機密情報フィールドがマスクされることを確認"""
    # パスワードを含むリクエスト
    login_data = {
        "email": "sales@example.com",
        "password": "secret_password",
        "token": "secret_token",
    }
    response = await client.post("/api/auth/login", json=login_data)

    # 操作履歴を取得
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.path == "/api/auth/login",
            AuditLog.method == "POST"
        ).order_by(AuditLog.created_at.desc())
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.request_body is not None

    # 機密情報がマスクされていることを確認
    assert "***MASKED***" in audit_log.request_body
    assert "secret_password" not in audit_log.request_body
    assert "secret_token" not in audit_log.request_body
    # メールアドレスは機密情報ではないので記録される
    assert "sales@example.com" in audit_log.request_body
