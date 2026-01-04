"""
FastAPI アプリケーション メインエントリーポイント
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.scheduler import start_scheduler
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    global scheduler
    # 起動時
    logger.info("アプリケーション起動: スケジューラーを開始します")
    scheduler = start_scheduler()
    yield
    # 終了時
    logger.info("アプリケーション終了: スケジューラーを停止します")
    if scheduler:
        scheduler.shutdown()


# FastAPIアプリケーション
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="営業日報システム API",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ルーター追加
from app.routers import (
    auth,
    companies,
    users,
    branches,
    departments,
    customers,
    daily_reports,
    subscriptions,
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(branches.router)
app.include_router(departments.router)
app.include_router(customers.router)
app.include_router(daily_reports.router)
app.include_router(subscriptions.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
