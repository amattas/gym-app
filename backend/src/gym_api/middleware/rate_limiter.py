import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

DEFAULT_LIMITS = {
    "/v1/auth/login": (10, 60),
    "/v1/auth/register": (10, 60),
    "/v1/auth/refresh": (20, 60),
    "/v1/auth/password-reset": (3, 3600),
}
API_LIMIT = (100, 60)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"{client_ip}:{path}"

        max_requests, window = DEFAULT_LIMITS.get(path, API_LIMIT)

        now = time.monotonic()
        bucket = self._buckets.setdefault(key, [])
        bucket[:] = [t for t in bucket if now - t < window]

        remaining = max_requests - len(bucket)

        if remaining <= 0:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests",
                        "details": [],
                    },
                    "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
                },
                headers={
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(window - (now - bucket[0]))) if bucket else "0",
                    "Retry-After": str(int(window - (now - bucket[0]))) if bucket else str(window),
                },
            )

        bucket.append(now)
        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        return response
