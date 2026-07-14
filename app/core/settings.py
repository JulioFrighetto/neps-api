from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./neps.db"
    APP_NAME: str = "Neps API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
        ]
    )

    ADMIN_NAME: str = "Admin"
    ADMIN_EMAIL: str = "alexdonay@gmail.com"
    ADMIN_PASSWORD: str = "secret123"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_FROM_NAME: str = "NEPS API"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    MAILERSEND_API_TOKEN: str | None = None
    MAILERSEND_FROM_EMAIL: str | None = None
    MAILERSEND_FROM_NAME: str = "NEPS API"

    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str | None = None
    SENDGRID_FROM_NAME: str = "NEPS API"

    mailersend_api_token: str | None = None
    mailersend_from_email: str | None = None
    mailersend_from_name: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
