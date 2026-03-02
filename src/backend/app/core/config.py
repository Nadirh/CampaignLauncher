from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FRONTEND_URL: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    SENTRY_DSN: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://campaignlauncher:campaignlauncher@localhost:5432/campaignlauncher"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
