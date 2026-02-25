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


def _make_template(**overrides):
    defaults = dict(
        plan_template_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="Monthly Unlimited",
        description="Unlimited access",
        plan_type="membership",
        status="active",
        visit_entitlement=None,
        plan_duration={"months": 1},
        payment_config=None,
        modules_enabled=None,
        is_addon=False,
        requires_primary_plan_type=None,
        addon_discount_percentage=None,
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
async def test_create_plan_template(client):
    t = _make_template()
    with patch(
        "gym_api.routers.plan_templates.plan_template_service.create_plan_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = t
        resp = await client.post(
            "/v1/plan-templates",
            json={"name": "Monthly Unlimited", "plan_type": "membership"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Monthly Unlimited"


@pytest.mark.asyncio
async def test_list_plan_templates(client):
    templates = [_make_template(), _make_template(name="10-Pack")]
    with patch(
        "gym_api.routers.plan_templates.plan_template_service.list_plan_templates",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (templates, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/plan-templates")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_plan_template(client):
    t = _make_template()
    with patch(
        "gym_api.routers.plan_templates.plan_template_service.get_plan_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = t
        resp = await client.get(f"/v1/plan-templates/{t.plan_template_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["plan_type"] == "membership"


@pytest.mark.asyncio
async def test_get_plan_template_not_found(client):
    with patch(
        "gym_api.routers.plan_templates.plan_template_service.get_plan_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/plan-templates/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_plan_template(client):
    t = _make_template()
    updated = _make_template(name="Updated Plan")
    with (
        patch(
            "gym_api.routers.plan_templates.plan_template_service.get_plan_template",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.plan_templates.plan_template_service.update_plan_template",
            new_callable=AsyncMock,
        ) as upd_mock,
    ):
        get_mock.return_value = t
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/plan-templates/{t.plan_template_id}",
            json={"name": "Updated Plan"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Plan"


@pytest.mark.asyncio
async def test_delete_plan_template(client):
    t = _make_template()
    with (
        patch(
            "gym_api.routers.plan_templates.plan_template_service.get_plan_template",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.plan_templates.plan_template_service.delete_plan_template",
            new_callable=AsyncMock,
        ),
    ):
        get_mock.return_value = t
        resp = await client.delete(f"/v1/plan-templates/{t.plan_template_id}")
    assert resp.status_code == 204
