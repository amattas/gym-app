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


def _make_trainer(**overrides):
    defaults = dict(
        trainer_id=uuid.uuid4(),
        gym_id=GYM_ID,
        user_id=None,
        first_name="Mike",
        last_name="Trainer",
        email="mike@gym.com",
        specializations="Strength",
        is_active=True,
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
async def test_create_trainer(client):
    t = _make_trainer()
    with patch(
        "gym_api.routers.trainers.trainer_service.create_trainer", new_callable=AsyncMock
    ) as mock:
        mock.return_value = t
        resp = await client.post(
            "/v1/trainers",
            json={"first_name": "Mike", "last_name": "Trainer", "email": "mike@gym.com"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["first_name"] == "Mike"


@pytest.mark.asyncio
async def test_list_trainers(client):
    trainers = [_make_trainer(), _make_trainer(first_name="Sarah")]
    with patch(
        "gym_api.routers.trainers.trainer_service.list_trainers", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (trainers, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/trainers")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_trainer(client):
    t = _make_trainer()
    with patch(
        "gym_api.routers.trainers.trainer_service.get_trainer", new_callable=AsyncMock
    ) as mock:
        mock.return_value = t
        resp = await client.get(f"/v1/trainers/{t.trainer_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_trainer_not_found(client):
    with patch(
        "gym_api.routers.trainers.trainer_service.get_trainer", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/trainers/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_trainer(client):
    t = _make_trainer()
    updated = _make_trainer(specializations="CrossFit")
    with (
        patch(
            "gym_api.routers.trainers.trainer_service.get_trainer", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.trainers.trainer_service.update_trainer", new_callable=AsyncMock
        ) as upd_mock,
    ):
        get_mock.return_value = t
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/trainers/{t.trainer_id}",
            json={"specializations": "CrossFit"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["specializations"] == "CrossFit"
