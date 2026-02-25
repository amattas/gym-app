import logging
import time

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# In-memory metrics for MVP (Prometheus client can be added for production)
_request_count: dict[str, int] = {}
_request_duration_sum: dict[str, float] = {}
_request_errors: dict[str, int] = {}


def _metric_key(method: str, path: str, status: int) -> str:
    return f"{method}:{path}:{status}"


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - start

        key = _metric_key(request.method, request.url.path, response.status_code)
        _request_count[key] = _request_count.get(key, 0) + 1
        _request_duration_sum[key] = _request_duration_sum.get(key, 0.0) + duration

        if response.status_code >= 500:
            err_key = _metric_key(request.method, request.url.path, response.status_code)
            _request_errors[err_key] = _request_errors.get(err_key, 0) + 1

        return response


def get_metrics_summary() -> dict:
    return {
        "request_count": dict(_request_count),
        "request_duration_sum": dict(_request_duration_sum),
        "request_errors": dict(_request_errors),
    }


def reset_metrics() -> None:
    _request_count.clear()
    _request_duration_sum.clear()
    _request_errors.clear()


def setup_metrics(app: FastAPI) -> None:
    app.add_middleware(MetricsMiddleware)
    logger.info("Metrics middleware installed")
