"""应用配置管理，基于 pydantic-settings 从环境变量加载"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── 应用 ──
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"

    # ── 数据库 ──
    DATABASE_URL: str = "postgresql+asyncpg://ft_user:ft_dev_password@localhost:5432/foreign_trade"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Elasticsearch ──
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # ── JWT 认证 ──
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── AI (DeepSeek) ──
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    AI_MAX_TOKENS: int = 4096
    AI_TEMPERATURE: float = 0.3
    AI_TIMEOUT: int = 60

    # ── Gmail OAuth ──
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/email-auth/gmail/callback"

    # ── 邮件发送 ──
    EMAIL_SEND_INTERVAL_SECONDS: int = 45    # 默认 45 秒/封
    EMAIL_DAILY_QUOTA: int = 450             # 默认日配额（留余量）

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
