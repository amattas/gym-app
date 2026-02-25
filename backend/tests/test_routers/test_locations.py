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
LOCATION_ID = uuid.uuid4()


def _make_location(**overrides):
    defaults = dict(
        location_id=LOCATION_ID,
        gym_id=GYM_ID,
        name="Main Floor",
        address="123 Fitness Ave",
        city="Portland",
        state="OR",
        postal_code="97201",
        country="US",
        timezone="America/Los_Angeles",
        capacity=100,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
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
async def test_create_location(client):
    loc = _make_location()
    with patch(
        "gym_api.routers.locations.location_service.create_location",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = loc
        resp = await client.post(
            f"/v1/gyms/{GYM_ID}/locations",
            json={"name": "Main Floor", "city": "Portland"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Main Floor"


@pytest.mark.asyncio
async def test_list_locations(client):
    locations = [_make_location(), _make_location(name="Pool Area")]
    with patch(
        "gym_api.routers.locations.location_service.list_locations",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (locations, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/gyms/{GYM_ID}/locations")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_location(client):
    loc = _make_location()
    with patch(
        "gym_api.routers.locations.location_service.get_location",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = loc
        resp = await client.get(f"/v1/locations/{LOCATION_ID}")
    assert resp.status_code == 200
    assert resp.json()["data"]["location_id"] == str(LOCATION_ID)


@pytest.mark.asyncio
async def test_get_location_not_found(client):
    with patch(
        "gym_api.routers.locations.location_service.get_location",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/locations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_location(client):
    loc = _make_location()
    updated = _make_location(name="Updated Floor")
    with (
        patch(
            "gym_api.routers.locations.location_service.get_location",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.locations.location_service.update_location",
            new_callable=AsyncMock,
        ) as update_mock,
    ):
        get_mock.return_value = loc
        update_mock.return_value = updated
        resp = await client.put(
            f"/v1/locations/{LOCATION_ID}",
            json={"name": "Updated Floor"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Floor"


@pytest.mark.asyncio
async def test_delete_location(client):
    loc = _make_location()
    with (
        patch(
            "gym_api.routers.locations.location_service.get_location",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.locations.location_service.delete_location",
            new_callable=AsyncMock,
        ) as del_mock,
    ):
        get_mock.return_value = loc
        del_mock.return_value = None
        resp = await client.delete(f"/v1/locations/{LOCATION_ID}")
    assert resp.status_code == 204
