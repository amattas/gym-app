from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from gym_api.config import settings


def create_https_redirect_middleware(app: FastAPI) -> None:
    if settings.enforce_https:
        app.add_middleware(HTTPSRedirectMiddleware)
