import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_metric(**overrides):
    defaults = dict(
        rollup_id=uuid.uuid4(),
        gym_id=GYM_ID,
        metric_name="active_clients",
        period_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        period_end=datetime(2026, 2, 1, tzinfo=timezone.utc),
        value=42,
        limit_value=100,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_usage(client):
    metrics = [_make_metric()]
    with patch(
        "gym_api.routers.usage.usage_metering_service.get_usage_summary",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = metrics
        resp = await client.get("/v1/usage")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["metric_name"] == "active_clients"


@pytest.mark.asyncio
async def test_get_usage_totals(client):
    with patch(
        "gym_api.routers.usage.usage_metering_service.get_metric_totals",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = [
            {"metric_name": "active_clients", "total": 42, "limit": 100},
        ]
        resp = await client.get("/v1/usage/totals")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["total"] == 42


@pytest.mark.asyncio
async def test_check_usage_limit(client):
    with patch(
        "gym_api.routers.usage.usage_metering_service.check_limit",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {"within_limit": True, "current": 42, "limit": 100}
        resp = await client.get("/v1/usage/check/active_clients")
    assert resp.status_code == 200
    assert resp.json()["data"]["within_limit"] is True
