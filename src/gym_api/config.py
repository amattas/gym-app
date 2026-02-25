from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/gym"
    ai_summary_provider: str = "anthropic"
    ai_summary_model: str = "claude-sonnet-4-20250514"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
