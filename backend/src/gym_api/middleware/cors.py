from starlette.middleware.cors import CORSMiddleware

PLATFORM_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]


def create_cors_middleware(
    app, *, cors_allowed_origins: str = "", extra_origins: list[str] | None = None
):
    allowed = list(PLATFORM_ORIGINS)
    if cors_allowed_origins:
        allowed.extend(
            origin.strip() for origin in cors_allowed_origins.split(",") if origin.strip()
        )
    if extra_origins:
        allowed.extend(extra_origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )
