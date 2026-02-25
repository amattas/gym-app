import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from gym_api.models.user import UserRole
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()
CLIENT_ID = uuid.uuid4()


def _make_measurement(**overrides):
    defaults = dict(
        measurement_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        type="weight",
        value=85.5,
        unit="kg",
        bmi=24.5,
        measured_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_measurement(client):
    m = _make_measurement()
    with patch(
        "gym_api.routers.measurements.measurement_service.create_measurement",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = m
        resp = await client.post(
            "/v1/measurements",
            json={"client_id": str(CLIENT_ID), "type": "weight", "value": 85.5, "unit": "kg"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["value"] == 85.5
    assert resp.json()["data"]["bmi"] == 24.5


@pytest.mark.asyncio
async def test_list_measurements(client):
    measurements = [_make_measurement(), _make_measurement(type="body_fat", bmi=None)]
    with patch(
        "gym_api.routers.measurements.measurement_service.list_measurements", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (measurements, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/measurements")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_list_measurements_filter_client(client):
    m = _make_measurement()
    with patch(
        "gym_api.routers.measurements.measurement_service.list_measurements", new_callable=AsyncMock
    ) as mock:
        mock.return_value = ([m], {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/measurements?client_id={CLIENT_ID}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_measurement(client):
    m = _make_measurement()
    with patch(
        "gym_api.routers.measurements.measurement_service.get_measurement", new_callable=AsyncMock
    ) as mock:
        mock.return_value = m
        resp = await client.get(f"/v1/measurements/{m.measurement_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_measurement_not_found(client):
    with patch(
        "gym_api.routers.measurements.measurement_service.get_measurement", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/measurements/{uuid.uuid4()}")
    assert resp.status_code == 404
