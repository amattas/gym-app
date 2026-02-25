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
USER_ID = uuid.uuid4()
DEVICE_ID = uuid.uuid4()


def _make_device(**overrides):
    defaults = dict(
        device_token_id=DEVICE_ID,
        user_id=USER_ID,
        platform="ios",
        token="abc123token",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_preferences(**overrides):
    defaults = dict(
        preference_id=uuid.uuid4(),
        user_id=USER_ID,
        session_reminders=True,
        workout_updates=True,
        membership_alerts=True,
        marketing=False,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(user_id=USER_ID, role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_device(client):
    device = _make_device()
    with patch(
        "gym_api.routers.notifications.notification_service.register_device",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = device
        resp = await client.post(
            "/v1/devices",
            json={"platform": "ios", "token": "abc123token"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["platform"] == "ios"


@pytest.mark.asyncio
async def test_unregister_device(client):
    device = _make_device()
    with (
        patch(
            "gym_api.routers.notifications.notification_service.get_device",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.notifications.notification_service.unregister_device",
            new_callable=AsyncMock,
        ) as del_mock,
    ):
        get_mock.return_value = device
        del_mock.return_value = None
        resp = await client.delete(f"/v1/devices/{DEVICE_ID}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_unregister_device_not_found(client):
    with patch(
        "gym_api.routers.notifications.notification_service.get_device",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.delete(f"/v1/devices/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_preferences(client):
    pref = _make_preferences()
    with patch(
        "gym_api.routers.notifications.notification_service.get_preferences",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = pref
        resp = await client.get("/v1/notifications/preferences")
    assert resp.status_code == 200
    assert resp.json()["data"]["session_reminders"] is True


@pytest.mark.asyncio
async def test_update_preferences(client):
    pref = _make_preferences(marketing=True)
    with patch(
        "gym_api.routers.notifications.notification_service.update_preferences",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = pref
        resp = await client.put(
            "/v1/notifications/preferences",
            json={"marketing": True},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["marketing"] is True
