import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from gym_api.cache.cache_service import get_redis

logger = logging.getLogger(__name__)

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

        remaining, reset_after = await self._check_rate_limit(key, max_requests, window)

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
                    "X-RateLimit-Reset": str(reset_after),
                    "Retry-After": str(reset_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        return response

    async def _check_rate_limit(
        self, key: str, max_requests: int, window: int
    ) -> tuple[int, int]:
        redis = await get_redis()
        if redis:
            return await self._check_redis(redis, key, max_requests, window)
        return self._check_memory(key, max_requests, window)

    async def _check_redis(
        self, redis, key: str, max_requests: int, window: int
    ) -> tuple[int, int]:
        redis_key = f"ratelimit:{key}"
        try:
            count = await redis.incr(redis_key)
            if count == 1:
                await redis.expire(redis_key, window)
            ttl = await redis.ttl(redis_key)
            # Return pre-request remaining (matching memory path convention).
            # dispatch() subtracts 1 to get post-request remaining.
            remaining = max_requests - count + 1
            return max(remaining, 0), max(ttl, 0)
        except Exception:
            logger.warning("Redis rate limit check failed, falling back to memory")
            return self._check_memory(key, max_requests, window)

    def _check_memory(self, key: str, max_requests: int, window: int) -> tuple[int, int]:
        now = time.monotonic()
        bucket = self._buckets.setdefault(key, [])
        bucket[:] = [t for t in bucket if now - t < window]

        remaining = max_requests - len(bucket)
        reset_after = int(window - (now - bucket[0])) if bucket else window

        if remaining <= 0:
            return 0, reset_after

        bucket.append(now)
        return remaining, reset_after
