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
TEMPLATE_ID = uuid.uuid4()


def _make_membership(**overrides):
    defaults = dict(
        client_membership_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        plan_template_id=TEMPLATE_ID,
        plan_type="membership",
        status="active",
        started_at=datetime.now(timezone.utc),
        expires_at=None,
        visit_entitlement=None,
        visits_used_this_period=0,
        total_visits_remaining=None,
        current_period_start=datetime.now(timezone.utc),
        current_period_end=None,
        pause_info=None,
        cancellation_info=None,
        base_membership_id=None,
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
async def test_create_membership(client):
    m = _make_membership()
    with patch(
        "gym_api.routers.memberships.membership_service.create_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = m
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/memberships",
            json={"plan_template_id": str(TEMPLATE_ID)},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["plan_type"] == "membership"


@pytest.mark.asyncio
async def test_list_client_memberships(client):
    memberships = [_make_membership(), _make_membership(plan_type="punch_card")]
    with patch(
        "gym_api.routers.memberships.membership_service.list_client_memberships",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (memberships, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/clients/{CLIENT_ID}/memberships")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_membership(client):
    m = _make_membership()
    with patch(
        "gym_api.routers.memberships.membership_service.get_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = m
        resp = await client.get(f"/v1/memberships/{m.client_membership_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_membership_not_found(client):
    with patch(
        "gym_api.routers.memberships.membership_service.get_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/memberships/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_pause_membership(client):
    m = _make_membership()
    paused = _make_membership(
        status="paused",
        pause_info={"paused_at": datetime.now(timezone.utc).isoformat(), "reason": "Vacation"},
    )
    with (
        patch(
            "gym_api.routers.memberships.membership_service.get_membership",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.memberships.membership_service.pause_membership",
            new_callable=AsyncMock,
        ) as pause_mock,
    ):
        get_mock.return_value = m
        pause_mock.return_value = paused
        resp = await client.post(
            f"/v1/memberships/{m.client_membership_id}/pause",
            json={"reason": "Vacation"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "paused"


@pytest.mark.asyncio
async def test_unpause_membership(client):
    m = _make_membership(status="paused")
    unpaused = _make_membership(status="active")
    with (
        patch(
            "gym_api.routers.memberships.membership_service.get_membership",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.memberships.membership_service.unpause_membership",
            new_callable=AsyncMock,
        ) as unpause_mock,
    ):
        get_mock.return_value = m
        unpause_mock.return_value = unpaused
        resp = await client.post(f"/v1/memberships/{m.client_membership_id}/unpause")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_cancel_membership(client):
    m = _make_membership()
    cancelled = _make_membership(status="cancelled")
    with (
        patch(
            "gym_api.routers.memberships.membership_service.get_membership",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.memberships.membership_service.cancel_membership",
            new_callable=AsyncMock,
        ) as cancel_mock,
    ):
        get_mock.return_value = m
        cancel_mock.return_value = cancelled
        resp = await client.post(
            f"/v1/memberships/{m.client_membership_id}/cancel",
            json={"reason": "Moving away", "cancel_immediately": True},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_get_entitlements(client):
    m = _make_membership(
        visit_entitlement={"visits_per_period": 12},
        visits_used_this_period=3,
        total_visits_remaining=9,
    )
    with patch(
        "gym_api.routers.memberships.membership_service.get_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = m
        resp = await client.get(f"/v1/memberships/{m.client_membership_id}/entitlements")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["visits_used_this_period"] == 3
    assert data["total_visits_remaining"] == 9


@pytest.mark.asyncio
async def test_record_visit(client):
    m = _make_membership()
    visited = _make_membership(visits_used_this_period=1)
    with (
        patch(
            "gym_api.routers.memberships.membership_service.get_membership",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.memberships.membership_service.record_visit",
            new_callable=AsyncMock,
        ) as visit_mock,
    ):
        get_mock.return_value = m
        visit_mock.return_value = visited
        resp = await client.post(
            f"/v1/memberships/{m.client_membership_id}/record-visit",
            json={"notes": "Morning session"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["visits_used_this_period"] == 1


@pytest.mark.asyncio
async def test_create_membership_validation_error(client):
    with patch(
        "gym_api.routers.memberships.membership_service.create_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.side_effect = ValueError("Plan template not found")
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/memberships",
            json={"plan_template_id": str(uuid.uuid4())},
        )
    assert resp.status_code == 400
    assert "Plan template not found" in resp.json()["error"]["message"]
