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
ACCOUNT_ID = uuid.uuid4()


def _make_account(**overrides):
    defaults = dict(
        account_id=ACCOUNT_ID,
        gym_id=GYM_ID,
        account_type="individual",
        billing_email="john@example.com",
        billing_address=None,
        stripe_customer_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_member(**overrides):
    defaults = dict(
        client_id=uuid.uuid4(),
        gym_id=GYM_ID,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone=None,
        date_of_birth=None,
        gender=None,
        status="active",
        account_id=ACCOUNT_ID,
        member_role="member",
        relationship_to_primary="spouse",
        login_enabled=True,
        primary_location_id=None,
        notes=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
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
async def test_create_account(client):
    account = _make_account()
    with patch(
        "gym_api.routers.accounts.account_service.create_account",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = account
        resp = await client.post(
            "/v1/accounts",
            json={"account_type": "individual", "billing_email": "john@example.com"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["billing_email"] == "john@example.com"


@pytest.mark.asyncio
async def test_get_account(client):
    account = _make_account()
    with patch(
        "gym_api.routers.accounts.account_service.get_account",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = account
        resp = await client.get(f"/v1/accounts/{ACCOUNT_ID}")
    assert resp.status_code == 200
    assert resp.json()["data"]["account_id"] == str(ACCOUNT_ID)


@pytest.mark.asyncio
async def test_get_account_not_found(client):
    with patch(
        "gym_api.routers.accounts.account_service.get_account",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/accounts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_members(client):
    members = [_make_member(), _make_member(first_name="Jim")]
    with patch(
        "gym_api.routers.accounts.account_service.list_account_members",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = members
        resp = await client.get(f"/v1/accounts/{ACCOUNT_ID}/members")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2
