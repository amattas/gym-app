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
WEBHOOK_ID = uuid.uuid4()


def _make_webhook(**overrides):
    defaults = dict(
        webhook_endpoint_id=WEBHOOK_ID,
        gym_id=GYM_ID,
        url="https://example.com/webhook",
        events=["client.created", "workout.completed"],
        is_active=True,
        created_at=datetime.now(timezone.utc).isoformat(),
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
async def test_create_webhook(client):
    webhook = _make_webhook()
    with patch(
        "gym_api.routers.webhook_endpoints.webhook_endpoint_service.create_webhook",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = webhook
        resp = await client.post(
            f"/v1/gyms/{GYM_ID}/webhooks",
            json={"url": "https://example.com/webhook", "events": ["client.created"]},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["url"] == "https://example.com/webhook"


@pytest.mark.asyncio
async def test_list_webhooks(client):
    webhooks = [_make_webhook(), _make_webhook(url="https://other.com/hook")]
    with patch(
        "gym_api.routers.webhook_endpoints.webhook_endpoint_service.list_webhooks",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = webhooks
        resp = await client.get(f"/v1/gyms/{GYM_ID}/webhooks")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_update_webhook(client):
    webhook = _make_webhook()
    updated = _make_webhook(url="https://updated.com/hook")
    with (
        patch(
            "gym_api.routers.webhook_endpoints.webhook_endpoint_service.get_webhook",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.webhook_endpoints.webhook_endpoint_service.update_webhook",
            new_callable=AsyncMock,
        ) as upd_mock,
    ):
        get_mock.return_value = webhook
        upd_mock.return_value = updated
        resp = await client.put(
            f"/v1/webhooks/{WEBHOOK_ID}",
            json={"url": "https://updated.com/hook"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["url"] == "https://updated.com/hook"


@pytest.mark.asyncio
async def test_delete_webhook(client):
    webhook = _make_webhook()
    with (
        patch(
            "gym_api.routers.webhook_endpoints.webhook_endpoint_service.get_webhook",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.webhook_endpoints.webhook_endpoint_service.delete_webhook",
            new_callable=AsyncMock,
        ) as del_mock,
    ):
        get_mock.return_value = webhook
        del_mock.return_value = None
        resp = await client.delete(f"/v1/webhooks/{WEBHOOK_ID}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_webhook_not_found(client):
    with patch(
        "gym_api.routers.webhook_endpoints.webhook_endpoint_service.get_webhook",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.delete(f"/v1/webhooks/{uuid.uuid4()}")
    assert resp.status_code == 404
