import json
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.cache import cache_service


@pytest.fixture(autouse=True)
def reset_redis():
    cache_service._redis = None
    yield
    cache_service._redis = None


async def test_get_redis_returns_none_on_failure():
    with patch.object(cache_service, "settings") as mock_settings:
        mock_settings.redis_url = "redis://invalid:9999"
        with patch("redis.asyncio.from_url", side_effect=Exception("connection refused")):
            result = await cache_service.get_redis()
            assert result is None


async def test_cache_get_returns_none_when_no_redis():
    result = await cache_service.cache_get("some_key")
    assert result is None


async def test_cache_get_returns_data():
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=json.dumps({"name": "test"}).encode())
    cache_service._redis = mock_redis

    result = await cache_service.cache_get("key1")
    assert result == {"name": "test"}
    mock_redis.get.assert_called_once_with("key1")


async def test_cache_set_returns_false_when_no_redis():
    result = await cache_service.cache_set("key", {"val": 1})
    assert result is False


async def test_cache_set_stores_data():
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()
    cache_service._redis = mock_redis

    result = await cache_service.cache_set("key1", {"val": 1}, ttl_seconds=60)
    assert result is True
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[0] == "key1"
    assert args[1] == 60


async def test_cache_delete_returns_false_when_no_redis():
    result = await cache_service.cache_delete("key")
    assert result is False


async def test_cache_delete_removes_key():
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock()
    cache_service._redis = mock_redis

    result = await cache_service.cache_delete("key1")
    assert result is True
    mock_redis.delete.assert_called_once_with("key1")


async def test_close_redis():
    mock_redis = AsyncMock()
    mock_redis.aclose = AsyncMock()
    cache_service._redis = mock_redis

    await cache_service.close_redis()
    assert cache_service._redis is None
    mock_redis.aclose.assert_called_once()
