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
SUMMARY_ID = uuid.uuid4()


def _make_summary(**overrides):
    defaults = dict(
        summary_id=SUMMARY_ID,
        client_id=CLIENT_ID,
        gym_id=GYM_ID,
        content="Client has shown great improvement in bench press over the last 4 weeks.",
        model_used="claude-3-opus",
        generated_at=datetime.now(timezone.utc).isoformat(),
        is_stale=False,
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
async def test_get_client_summary(client):
    summary = _make_summary()
    with patch(
        "gym_api.routers.ai_summaries.ai_summary_service.get_client_summary",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = summary
        resp = await client.get(f"/v1/clients/{CLIENT_ID}/ai-summary")
    assert resp.status_code == 200
    assert "bench press" in resp.json()["data"]["content"]


@pytest.mark.asyncio
async def test_get_client_summary_not_found(client):
    with patch(
        "gym_api.routers.ai_summaries.ai_summary_service.get_client_summary",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/clients/{uuid.uuid4()}/ai-summary")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_regenerate_summary(client):
    summary = _make_summary(content="AI summary generation pending", model_used="pending")
    with patch(
        "gym_api.routers.ai_summaries.ai_summary_service.create_summary",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = summary
        resp = await client.post(f"/v1/clients/{CLIENT_ID}/ai-summary/regenerate")
    assert resp.status_code == 200
    assert resp.json()["data"]["content"] == "AI summary generation pending"


@pytest.mark.asyncio
async def test_update_summary(client):
    summary = _make_summary()
    updated = _make_summary(content="Updated trainer review.")
    with (
        patch(
            "gym_api.routers.ai_summaries.ai_summary_service.get_summary_by_id",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.ai_summaries.ai_summary_service.update_summary",
            new_callable=AsyncMock,
        ) as upd_mock,
    ):
        get_mock.return_value = summary
        upd_mock.return_value = updated
        resp = await client.put(
            f"/v1/ai-summaries/{SUMMARY_ID}",
            json={"content": "Updated trainer review."},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["content"] == "Updated trainer review."


@pytest.mark.asyncio
async def test_update_summary_not_found(client):
    with patch(
        "gym_api.routers.ai_summaries.ai_summary_service.get_summary_by_id",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.put(
            f"/v1/ai-summaries/{uuid.uuid4()}",
            json={"content": "test"},
        )
    assert resp.status_code == 404
