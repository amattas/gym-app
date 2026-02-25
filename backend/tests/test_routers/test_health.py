from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_liveness_always_ok(client):
    resp = await client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_all_healthy(client):
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock()
    mock_redis.aclose = AsyncMock()

    with (
        patch("gym_api.routers.health.async_session", return_value=mock_session),
        patch("redis.asyncio.from_url", return_value=mock_redis),
    ):
        resp = await client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["postgresql"] == "ok"
    assert body["checks"]["redis"] == "ok"


@pytest.mark.asyncio
async def test_readiness_postgres_down(client):
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(side_effect=ConnectionError("pg down"))
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock()
    mock_redis.aclose = AsyncMock()

    with (
        patch("gym_api.routers.health.async_session", return_value=mock_session),
        patch("redis.asyncio.from_url", return_value=mock_redis),
    ):
        resp = await client.get("/health/ready")
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["postgresql"] == "unavailable"


@pytest.mark.asyncio
async def test_readiness_redis_down(client):
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("gym_api.routers.health.async_session", return_value=mock_session),
        patch("redis.asyncio.from_url", side_effect=ConnectionError("redis down")),
    ):
        resp = await client.get("/health/ready")
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"] == "unavailable"
