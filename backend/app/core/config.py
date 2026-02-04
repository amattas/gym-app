"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = "Gym App API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")

    # API settings
    api_v1_prefix: str = "/api/v1"
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # CORS settings
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # PostgreSQL settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "gym_app"
    postgres_password: str = "gym_app_password"
    postgres_db: str = "gym_app"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20

    @property
    def postgres_dsn(self) -> str:
        """Construct PostgreSQL connection string."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_dsn_sync(self) -> str:
        """Construct synchronous PostgreSQL connection string for Alembic."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # MongoDB settings
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_user: str = ""
    mongodb_password: str = ""
    mongodb_db: str = "gym_app"
    mongodb_auth_source: str = "admin"

    @property
    def mongodb_dsn(self) -> str:
        """Construct MongoDB connection string."""
        if self.mongodb_user and self.mongodb_password:
            return (
                f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
                f"@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
                f"?authSource={self.mongodb_auth_source}"
            )
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_ssl: bool = False

    @property
    def redis_dsn(self) -> str:
        """Construct Redis connection string."""
        protocol = "rediss" if self.redis_ssl else "redis"
        if self.redis_password:
            return f"{protocol}://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"{protocol}://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Rate limiting settings
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Account lockout settings
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30

    # Email settings (SMTP fallback)
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_email: str = "noreply@gymapp.com"
    from_name: str = "Gym App"
    frontend_url: str = "http://localhost:3000"

    # Resend email service (preferred)
    resend_api_key: str = ""

    # Verification token settings
    verification_token_expiry_hours: int = 24

    # S3/Object Storage settings
    s3_endpoint_url: str | None = None  # For MinIO or S3-compatible services
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "us-east-1"
    s3_bucket_name: str = "gym-app-photos"
    s3_use_ssl: bool = True

    # Auto-attendance settings
    auto_attendance_tolerance_minutes: int = Field(
        default=15,
        description="Time tolerance in minutes for auto-attendance matching (before/after session)",
    )
    auto_attendance_enabled: bool = Field(
        default=True,
        description="Whether to enable automatic attendance marking when exercises are logged",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
