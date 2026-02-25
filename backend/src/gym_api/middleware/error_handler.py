import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _error_body(code: str, message: str, request_id: str, details: list | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        },
        "meta": {"request_id": request_id},
    }


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception:
            rid = _request_id(request)
            logger.exception("Unhandled exception [request_id=%s]", rid)
            return JSONResponse(
                status_code=500,
                content=_error_body(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred",
                    request_id=rid,
                ),
            )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            request_id=_request_id(request),
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]} for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_error_body(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=_request_id(request),
            details=details,
        ),
    )
