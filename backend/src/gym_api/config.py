import warnings

from pydantic_settings import BaseSettings

_INSECURE_JWT_DEFAULTS = {"change-me-in-production", "secret", ""}


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/gym"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    debug: bool = False
    enforce_https: bool = False
    frontend_url: str = "http://localhost:3000"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@gymplatform.io"
    cors_allowed_origins: str = ""

    model_config = {"env_prefix": "", "env_file": ".env"}

    def validate_jwt_secret(self) -> None:
        if self.jwt_secret in _INSECURE_JWT_DEFAULTS or len(self.jwt_secret) < 32:
            if self.debug:
                warnings.warn(
                    "JWT secret is insecure. Set JWT_SECRET to a strong value before deploying.",
                    stacklevel=2,
                )
            else:
                raise ValueError(
                    "JWT_SECRET is not set or is insecure. "
                    "Set a strong JWT_SECRET (32+ characters) in environment variables."
                )


settings = Settings()
