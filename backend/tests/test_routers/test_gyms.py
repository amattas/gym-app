import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from gym_api.models.user import UserRole
from tests.test_routers.helpers import make_mock_user


def _make_gym(**overrides):
    defaults = dict(
        gym_id=uuid.uuid4(),
        name="Test Gym",
        slug="test-gym",
        unit_system="imperial",
        timezone="America/New_York",
        is_active=True,
        settings=None,
        contact_email="info@test.com",
        contact_phone=None,
        address=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_create_gym(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user
    gym = _make_gym()

    with patch("gym_api.routers.gyms.gym_service.create_gym", new_callable=AsyncMock) as mock:
        mock.return_value = gym
        resp = await client.post(
            "/v1/gyms",
            json={"name": "Test Gym", "slug": "test-gym"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Test Gym"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_gym_duplicate_slug(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user

    with patch("gym_api.routers.gyms.gym_service.create_gym", new_callable=AsyncMock) as mock:
        mock.side_effect = ValueError("Gym slug already exists")
        resp = await client.post(
            "/v1/gyms",
            json={"name": "Test", "slug": "dup"},
        )
    assert resp.status_code == 409
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_gyms(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user
    gyms = [_make_gym(name="Gym A"), _make_gym(name="Gym B")]

    with patch("gym_api.routers.gyms.gym_service.list_gyms", new_callable=AsyncMock) as mock:
        mock.return_value = (gyms, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/gyms")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_gym(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user
    gym = _make_gym()

    with patch("gym_api.routers.gyms.gym_service.get_gym", new_callable=AsyncMock) as mock:
        mock.return_value = gym
        resp = await client.get(f"/v1/gyms/{gym.gym_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["slug"] == "test-gym"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_gym_not_found(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user

    with patch("gym_api.routers.gyms.gym_service.get_gym", new_callable=AsyncMock) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/gyms/{uuid.uuid4()}")
    assert resp.status_code == 404
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_gym(client):
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    app.dependency_overrides[get_current_user] = lambda: user
    gym = _make_gym()
    updated = _make_gym(name="Updated Gym")

    with (
        patch("gym_api.routers.gyms.gym_service.get_gym", new_callable=AsyncMock) as get_mock,
        patch("gym_api.routers.gyms.gym_service.update_gym", new_callable=AsyncMock) as upd_mock,
    ):
        get_mock.return_value = gym
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/gyms/{gym.gym_id}",
            json={"name": "Updated Gym"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Gym"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_gym_forbidden_for_non_admin(client):
    user = make_mock_user(role=UserRole.client)
    app.dependency_overrides[get_current_user] = lambda: user

    resp = await client.post(
        "/v1/gyms",
        json={"name": "Test", "slug": "test"},
    )
    assert resp.status_code == 403
    app.dependency_overrides.clear()
