from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TurnosPro"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-super-secret-key-in-production-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/turnospro"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ]

    # n8n
    N8N_WEBHOOK_BASE_URL: str = "https://your-n8n-instance.app.n8n.cloud/webhook"
    N8N_APPOINTMENT_CREATED_WEBHOOK: str = "/appointment-created"
    N8N_APPOINTMENT_CANCELLED_WEBHOOK: str = "/appointment-cancelled"

    # Public URL (para links mágicos)
    PUBLIC_FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
