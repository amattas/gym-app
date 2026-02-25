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
LOCATION_ID = uuid.uuid4()
CHECK_IN_ID = uuid.uuid4()


def _make_check_in(**overrides):
    defaults = dict(
        check_in_id=CHECK_IN_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        location_id=LOCATION_ID,
        schedule_id=None,
        check_in_method="manual",
        checked_in_by_user_id=uuid.uuid4(),
        checked_in_at=datetime.now(timezone.utc),
        checked_out_at=None,
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
async def test_create_check_in(client):
    ci = _make_check_in()
    with patch(
        "gym_api.routers.check_ins.check_in_service.create_check_in",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = ci
        resp = await client.post(
            "/v1/check-ins",
            json={"client_id": str(CLIENT_ID), "location_id": str(LOCATION_ID)},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["check_in_method"] == "manual"


@pytest.mark.asyncio
async def test_list_check_ins(client):
    items = [_make_check_in(), _make_check_in(check_in_method="qr")]
    with patch(
        "gym_api.routers.check_ins.check_in_service.list_check_ins",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (items, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/check-ins")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_check_in_not_found(client):
    with patch(
        "gym_api.routers.check_ins.check_in_service.get_check_in",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/check-ins/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_checkout(client):
    ci = _make_check_in()
    checked_out = _make_check_in(checked_out_at=datetime.now(timezone.utc))
    with (
        patch(
            "gym_api.routers.check_ins.check_in_service.get_check_in",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.check_ins.check_in_service.checkout",
            new_callable=AsyncMock,
        ) as co_mock,
    ):
        get_mock.return_value = ci
        co_mock.return_value = checked_out
        resp = await client.post(f"/v1/check-ins/{CHECK_IN_ID}/checkout")
    assert resp.status_code == 200
    assert resp.json()["data"]["checked_out_at"] is not None


@pytest.mark.asyncio
async def test_get_occupancy(client):
    with patch(
        "gym_api.routers.check_ins.check_in_service.get_active_occupancy",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = 42
        resp = await client.get(f"/v1/locations/{LOCATION_ID}/occupancy")
    assert resp.status_code == 200
    assert resp.json()["data"]["active_count"] == 42
