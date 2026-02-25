import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from gym_api.models.user import UserRole
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_invitation(**overrides):
    defaults = dict(
        invitation_id=uuid.uuid4(),
        gym_id=GYM_ID,
        email="new.trainer@gym.com",
        token_hash="abc123",
        invited_by_user_id=uuid.uuid4(),
        is_used=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        created_at=datetime.now(timezone.utc),
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
async def test_create_invitation(client):
    inv = _make_invitation()
    with patch(
        "gym_api.routers.invitations.invitation_service.create_invitation",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (inv, "raw-setup-token")
        resp = await client.post(
            "/v1/invitations",
            json={"email": "new.trainer@gym.com"},
        )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["email"] == "new.trainer@gym.com"
    assert data["setup_token"] == "raw-setup-token"


@pytest.mark.asyncio
async def test_accept_invitation(client):
    inv = _make_invitation()
    mock_user = SimpleNamespace(
        user_id=uuid.uuid4(),
        email="new.trainer@gym.com",
        role=UserRole.trainer,
    )
    mock_trainer = SimpleNamespace(
        trainer_id=uuid.uuid4(),
        gym_id=GYM_ID,
        first_name="New",
        last_name="Trainer",
    )

    # Clear auth override for public endpoint
    app.dependency_overrides.clear()

    with (
        patch(
            "gym_api.routers.invitations.invitation_service.validate_invitation",
            new_callable=AsyncMock,
        ) as validate_mock,
        patch(
            "gym_api.routers.invitations.auth_service.register_user",
            new_callable=AsyncMock,
        ) as register_mock,
        patch(
            "gym_api.routers.invitations.create_trainer",
            new_callable=AsyncMock,
        ) as trainer_mock,
        patch(
            "gym_api.routers.invitations.invitation_service.accept_invitation",
            new_callable=AsyncMock,
        ),
    ):
        validate_mock.return_value = inv
        register_mock.return_value = mock_user
        trainer_mock.return_value = mock_trainer
        resp = await client.post(
            "/v1/invitations/accept",
            json={
                "token": "raw-token",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "Trainer",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "trainer"


@pytest.mark.asyncio
async def test_accept_invalid_invitation(client):
    app.dependency_overrides.clear()

    with patch(
        "gym_api.routers.invitations.invitation_service.validate_invitation",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.post(
            "/v1/invitations/accept",
            json={
                "token": "bad-token",
                "password": "SecurePass123!",
                "first_name": "X",
                "last_name": "Y",
            },
        )
    assert resp.status_code == 400
