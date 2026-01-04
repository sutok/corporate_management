"""
認証エンドポイント
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserResponse
from app.auth.password import verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/auth", tags=["認証"])


@router.post("/login")
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    ログイン

    Args:
        login_request: ログインリクエスト（email, password）
        db: データベースセッション

    Returns:
        アクセストークンとユーザー情報

    Raises:
        HTTPException: 認証に失敗した場合
    """
    # ユーザーをメールアドレスで検索
    result = await db.execute(
        select(User).where(User.email == login_request.email)
    )
    user = result.scalar_one_or_none()

    # ユーザーが存在しない、またはパスワードが一致しない場合
    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アクセストークンを生成
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    ログイン（フォーム形式）

    OAuth2PasswordRequestForm互換のエンドポイント
    Swagger UIの「Authorize」ボタンで使用される

    Args:
        form_data: OAuth2フォームデータ（username, password）
        db: データベースセッション

    Returns:
        アクセストークン
    """
    # usernameをemailとして扱う
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    現在のユーザー情報を取得

    Args:
        current_user: 現在のユーザー（依存性注入）

    Returns:
        現在のユーザー情報
    """
    return current_user
