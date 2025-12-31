"""
認証依存性注入
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.jwt import decode_access_token
from app.models.user import User

# OAuth2スキーム（トークンをAuthorizationヘッダーから取得）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    現在のユーザーを取得

    Args:
        token: JWTトークン
        db: データベースセッション

    Returns:
        現在のユーザー

    Raises:
        HTTPException: 認証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # トークンをデコード
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # ユーザーIDを取得
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # データベースからユーザーを取得
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    アクティブな現在のユーザーを取得

    Args:
        current_user: 現在のユーザー

    Returns:
        現在のユーザー

    Note:
        将来的にユーザーの有効/無効フラグを追加する場合に使用
    """
    return current_user
