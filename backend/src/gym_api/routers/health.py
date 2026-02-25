import logging

from fastapi import APIRouter
from sqlalchemy import text

from gym_api.database import async_session

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health/live")
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    checks = {}

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["postgresql"] = "ok"
    except Exception:
        logger.exception("PostgreSQL readiness check failed")
        checks["postgresql"] = "unavailable"

    try:
        import redis.asyncio as aioredis

        from gym_api.config import settings

        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception:
        logger.exception("Redis readiness check failed")
        checks["redis"] = "unavailable"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}
