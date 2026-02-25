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
EXPORT_ID = uuid.uuid4()
DELETION_ID = uuid.uuid4()


def _make_export_request(**overrides):
    defaults = dict(
        export_id=EXPORT_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        status="pending",
        format="json",
        download_url=None,
        requested_at=datetime.now(timezone.utc),
        completed_at=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_deletion_request(**overrides):
    defaults = dict(
        deletion_id=DELETION_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        status="pending",
        reason="Account closure",
        requested_at=datetime.now(timezone.utc),
        scheduled_for=datetime(2026, 4, 1, tzinfo=timezone.utc),
        completed_at=None,
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
async def test_create_data_export(client):
    export = _make_export_request()
    with patch(
        "gym_api.routers.data_privacy.data_export_service.create_export_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = export
        resp = await client.post(f"/v1/clients/{CLIENT_ID}/data-export")
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_get_export_status(client):
    export = _make_export_request(status="completed")
    with patch(
        "gym_api.routers.data_privacy.data_export_service.get_export_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = export
        resp = await client.get(f"/v1/data-exports/{EXPORT_ID}/status")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_get_export_status_not_found(client):
    with patch(
        "gym_api.routers.data_privacy.data_export_service.get_export_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/data-exports/{uuid.uuid4()}/status")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_export(client):
    export = _make_export_request(
        status="completed",
        download_url="https://storage.example.com/exports/file.json",
    )
    with patch(
        "gym_api.routers.data_privacy.data_export_service.get_export_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = export
        resp = await client.get(f"/v1/data-exports/{EXPORT_ID}/download")
    assert resp.status_code == 200
    assert "storage.example.com" in resp.json()["data"]["download_url"]


@pytest.mark.asyncio
async def test_download_export_not_ready(client):
    export = _make_export_request(status="processing", download_url=None)
    with patch(
        "gym_api.routers.data_privacy.data_export_service.get_export_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = export
        resp = await client.get(f"/v1/data-exports/{EXPORT_ID}/download")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_request_deletion(client):
    deletion = _make_deletion_request()
    with patch(
        "gym_api.routers.data_privacy.data_deletion_service.create_deletion_request",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = deletion
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/request-deletion",
            json={"reason": "Account closure"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["reason"] == "Account closure"
