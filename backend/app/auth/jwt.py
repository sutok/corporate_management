"""
JWTトークン処理ユーティリティ
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    アクセストークンを作成

    Args:
        data: トークンに含めるデータ（user_id, emailなど）
        expires_delta: トークンの有効期限（指定しない場合は設定値を使用）

    Returns:
        JWTトークン文字列
    """
    to_encode = data.copy()

    # 有効期限の設定
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # トークンの生成
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    アクセストークンをデコード

    Args:
        token: JWTトークン文字列

    Returns:
        トークンのペイロード（デコードに失敗した場合はNone）
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
