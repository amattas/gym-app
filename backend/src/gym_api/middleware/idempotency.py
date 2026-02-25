import hashlib
import json
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

HEADER = "X-Idempotency-Key"
IDEMPOTENT_METHODS = {"POST", "PUT", "PATCH"}
TTL_SECONDS = 86400  # 24 hours


class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._store: dict[str, dict] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in IDEMPOTENT_METHODS:
            return await call_next(request)

        key = request.headers.get(HEADER)
        if not key:
            return await call_next(request)

        cache_key = self._make_cache_key(key, request)
        self._evict_expired()

        if cache_key in self._store:
            cached = self._store[cache_key]
            return JSONResponse(
                status_code=cached["status_code"],
                content=cached["body"],
                headers={"X-Idempotent-Replayed": "true"},
            )

        response = await call_next(request)

        if 200 <= response.status_code < 500:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode()
            try:
                parsed = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed = body.decode(errors="replace")

            self._store[cache_key] = {
                "status_code": response.status_code,
                "body": parsed,
                "expires_at": time.monotonic() + TTL_SECONDS,
            }
            return JSONResponse(
                status_code=response.status_code,
                content=parsed,
                headers=dict(response.headers),
            )

        return response

    def _make_cache_key(self, key: str, request: Request) -> str:
        raw = f"{request.method}:{request.url.path}:{key}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _evict_expired(self):
        now = time.monotonic()
        expired = [k for k, v in self._store.items() if v["expires_at"] < now]
        for k in expired:
            del self._store[k]
