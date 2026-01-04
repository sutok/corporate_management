"""
Audit Logging Middleware
全てのAPIリクエストを操作履歴として記録するミドルウェア
"""
import json
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)

# ログに記録しないパス（ヘルスチェックなど）
EXCLUDED_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# リクエストボディからマスクする機密情報のキー
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
}


def mask_sensitive_data(data: dict) -> dict:
    """
    機密情報をマスクする

    Args:
        data: マスク対象のデータ

    Returns:
        マスク済みのデータ
    """
    if not isinstance(data, dict):
        return data

    masked_data = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked_data[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked_data[key] = value

    return masked_data


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """操作履歴記録ミドルウェア"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        リクエストを処理し、操作履歴を記録する

        Args:
            request: FastAPIリクエスト
            call_next: 次のミドルウェアまたはエンドポイント

        Returns:
            レスポンス
        """
        # 除外パスの場合はログを記録せずに次へ
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # 開始時刻を記録
        start_time = time.time()

        # ユーザー情報を取得（認証済みの場合）
        user_id = None
        company_id = None
        if hasattr(request.state, "user"):
            user_id = getattr(request.state.user, "id", None)
            company_id = getattr(request.state.user, "company_id", None)

        # リクエストボディを取得（JSONの場合のみ）
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_json = json.loads(body_bytes.decode("utf-8"))
                    # 機密情報をマスク
                    request_body = json.dumps(mask_sensitive_data(body_json))

                # リクエストボディを再度読めるようにする
                async def receive():
                    return {"type": "http.request", "body": body_bytes}

                request._receive = receive
            except (json.JSONDecodeError, UnicodeDecodeError):
                # JSONでない場合は記録しない
                pass
            except Exception as e:
                logger.warning(f"リクエストボディの取得に失敗: {e}")

        # クエリパラメータを取得
        query_params = None
        if request.query_params:
            query_params = json.dumps(dict(request.query_params))

        # IPアドレスを取得
        ip_address = request.client.host if request.client else None

        # User-Agentを取得
        user_agent = request.headers.get("user-agent")

        # レスポンスを処理
        response = await call_next(request)

        # 処理時間を計算
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        # 操作履歴を非同期で記録
        try:
            await self._log_audit(
                user_id=user_id,
                company_id=company_id,
                method=request.method,
                path=request.url.path,
                query_params=query_params,
                request_body=request_body,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            # ログ記録の失敗はアプリケーションの動作に影響を与えない
            logger.error(f"操作履歴の記録に失敗: {e}")

        return response

    async def _log_audit(
        self,
        user_id: int | None,
        company_id: int | None,
        method: str,
        path: str,
        query_params: str | None,
        request_body: str | None,
        status_code: int,
        response_time_ms: int,
        ip_address: str | None,
        user_agent: str | None,
    ):
        """
        操作履歴をデータベースに記録

        Args:
            各種リクエスト情報
        """
        async with AsyncSessionLocal() as db:
            try:
                audit_log = AuditLog(
                    user_id=user_id,
                    company_id=company_id,
                    method=method,
                    path=path,
                    query_params=query_params,
                    request_body=request_body,
                    status_code=status_code,
                    response_time_ms=response_time_ms,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                db.add(audit_log)
                await db.commit()
            except Exception as e:
                logger.error(f"操作履歴のDB保存に失敗: {e}")
                await db.rollback()
                raise
