import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user, require_role
from gym_api.main import app
from gym_api.models.user import UserRole
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_audit_log(**overrides):
    defaults = dict(
        audit_log_id=uuid.uuid4(),
        gym_id=GYM_ID,
        user_id=uuid.uuid4(),
        action="client.created",
        resource_type="client",
        resource_id=str(uuid.uuid4()),
        details={"name": "John Doe"},
        ip_address="127.0.0.1",
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user

    def _fake_require_role(*roles):
        return lambda: user

    override_key = require_role(UserRole.gym_admin, UserRole.platform_admin)
    app.dependency_overrides[override_key] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_audit_logs(client):
    logs = [_make_audit_log(), _make_audit_log(action="workout.completed")]
    with patch(
        "gym_api.routers.audit_logs.audit_service.list_audit_logs",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (logs, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/audit-logs")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_list_audit_logs_with_filters(client):
    logs = [_make_audit_log()]
    with patch(
        "gym_api.routers.audit_logs.audit_service.list_audit_logs",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (logs, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(
            "/v1/audit-logs?action=client.created&resource_type=client"
        )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
