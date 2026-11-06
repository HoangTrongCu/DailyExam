"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from env vars."""

    model_config = SettingsConfigDict(env_prefix="DAILYEXAM_", env_file=".env", extra="ignore")

    app_name: str = "DailyExam API"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    gate_open_hour: int = 8
    gate_close_hour: int = 9
    result_release_hour: int = 9
    result_release_minute: int = 30

    # Database
    database_url: str = "sqlite:///./dailyexam.db"

    # Auth
    jwt_secret: str = "change-me-in-production-very-long-secret-key-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-haiku-4-5"
    llm_mock_mode: bool = True  # Use rule-based grading when no API key


def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
