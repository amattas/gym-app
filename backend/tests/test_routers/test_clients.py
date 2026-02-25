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


def _make_client(**overrides):
    defaults = dict(
        client_id=uuid.uuid4(),
        gym_id=GYM_ID,
        user_id=None,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone=None,
        date_of_birth=None,
        gender=None,
        height_cm=None,
        weight_kg=None,
        fitness_goals=None,
        emergency_contact_name="John Doe",
        emergency_contact_phone="555-123-4567",
        status="active",
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
async def test_create_client(client):
    c = _make_client()
    with patch(
        "gym_api.routers.clients.client_service.create_client", new_callable=AsyncMock
    ) as mock:
        mock.return_value = c
        resp = await client.post(
            "/v1/clients",
            json={"first_name": "Jane", "last_name": "Doe"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_list_clients(client):
    clients_list = [_make_client(), _make_client(first_name="Bob")]
    with patch(
        "gym_api.routers.clients.client_service.list_clients", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (clients_list, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/clients")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_client(client):
    c = _make_client()
    with patch("gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock) as mock:
        mock.return_value = c
        resp = await client.get(f"/v1/clients/{c.client_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_client_not_found(client):
    with patch("gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/clients/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_client(client):
    c = _make_client()
    updated = _make_client(first_name="Janet")
    with (
        patch(
            "gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.clients.client_service.update_client", new_callable=AsyncMock
        ) as upd_mock,
    ):
        get_mock.return_value = c
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/clients/{c.client_id}",
            json={"first_name": "Janet"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["first_name"] == "Janet"


@pytest.mark.asyncio
async def test_delete_client(client):
    c = _make_client()
    with (
        patch(
            "gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.clients.client_service.delete_client", new_callable=AsyncMock
        ),
    ):
        get_mock.return_value = c
        resp = await client.delete(f"/v1/clients/{c.client_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_get_emergency_contact(client):
    c = _make_client()
    with patch("gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock) as mock:
        mock.return_value = c
        resp = await client.get(f"/v1/clients/{c.client_id}/emergency-contact")
    assert resp.status_code == 200
    assert resp.json()["data"]["emergency_contact_name"] == "John Doe"


@pytest.mark.asyncio
async def test_update_emergency_contact(client):
    c = _make_client()
    updated = _make_client(emergency_contact_name="Alice", emergency_contact_phone="555-999-0000")
    with (
        patch(
            "gym_api.routers.clients.client_service.get_client", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.clients.client_service.update_client", new_callable=AsyncMock
        ) as upd_mock,
    ):
        get_mock.return_value = c
        upd_mock.return_value = updated
        resp = await client.put(
            f"/v1/clients/{c.client_id}/emergency-contact",
            json={"emergency_contact_name": "Alice", "emergency_contact_phone": "555-999-0000"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["emergency_contact_name"] == "Alice"
