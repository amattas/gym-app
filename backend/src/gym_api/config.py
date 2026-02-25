from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/gym"
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = False

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
