import json
import logging

import redis.asyncio as aioredis

from gym_api.config import settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(settings.redis_url)
            await _redis.ping()
        except Exception:
            logger.warning("Redis unavailable, caching disabled")
            _redis = None
    return _redis


async def cache_get(key: str) -> dict | None:
    r = await get_redis()
    if not r:
        return None
    try:
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception:
        logger.warning("Cache get failed for key=%s", key)
    return None


async def cache_set(key: str, value: dict, ttl_seconds: int = 300) -> bool:
    r = await get_redis()
    if not r:
        return False
    try:
        await r.setex(key, ttl_seconds, json.dumps(value, default=str))
        return True
    except Exception:
        logger.warning("Cache set failed for key=%s", key)
    return False


async def cache_delete(key: str) -> bool:
    r = await get_redis()
    if not r:
        return False
    try:
        await r.delete(key)
        return True
    except Exception:
        logger.warning("Cache delete failed for key=%s", key)
    return False


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
