"""
アプリケーション設定管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """アプリケーション設定"""

    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "営業日報システム"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Timezone
    TIMEZONE: str = "Asia/Tokyo"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS許可オリジンをリストで取得"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """設定インスタンスを取得（シングルトン）"""
    return Settings()
