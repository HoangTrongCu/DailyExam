"""Application settings loaded from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DAILYEXAM_", env_file=".env", extra="ignore")

    app_name: str = "DailyExam API"
    environment: str = "development"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    base_url: str = "http://localhost:3001"

    # Database
    database_url: str = "sqlite:///./dailyexam.db"

    # Auth
    jwt_secret: str = "dev-only-secret-change-in-prod-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    verify_token_expire_hours: int = 24
    reset_token_expire_minutes: int = 15

    # Scheduler
    gate_open_hour: int = 8  # frontend display only; backend gates by created-day
    exam_gen_hour: int = 5

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-haiku-4-5"
    llm_mock_mode: bool = True

    # Email
    email_provider: str = "mock"  # mock | resend
    email_from: str = "DailyExam <no-reply@dailyexam.vn>"
    resend_api_key: str = ""


def get_settings() -> Settings:
    return Settings()
