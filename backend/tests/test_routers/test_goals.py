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
GOAL_ID = uuid.uuid4()
PROGRAM_ID = uuid.uuid4()
DAY_ID = uuid.uuid4()


def _make_goal(**overrides):
    defaults = dict(
        goal_id=GOAL_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        goal_type="weight_loss",
        target_value=75.0,
        current_value=85.0,
        target_date=None,
        status="active",
        notes=None,
        created_by_trainer_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_client_program(**overrides):
    defaults = dict(
        client_program_id=uuid.uuid4(),
        client_id=CLIENT_ID,
        program_id=PROGRAM_ID,
        status="active",
        assigned_at=datetime.now(timezone.utc),
        assigned_by_trainer_id=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_program_day(**overrides):
    defaults = dict(
        program_day_id=DAY_ID,
        program_id=PROGRAM_ID,
        name="Day 1 - Push",
        order_index=0,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_day_exercise(**overrides):
    defaults = dict(
        program_day_exercise_id=uuid.uuid4(),
        program_day_id=DAY_ID,
        exercise_id=uuid.uuid4(),
        order_index=0,
        default_sets=3,
        default_reps=10,
        rest_seconds=60,
        notes=None,
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
async def test_create_goal(client):
    goal = _make_goal()
    with patch(
        "gym_api.routers.goals.goal_service.create_goal",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = goal
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/goals",
            json={"goal_type": "weight_loss", "target_value": 75.0, "current_value": 85.0},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["goal_type"] == "weight_loss"


@pytest.mark.asyncio
async def test_list_goals(client):
    goals = [_make_goal(), _make_goal(goal_type="strength")]
    with patch(
        "gym_api.routers.goals.goal_service.list_client_goals",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (goals, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/clients/{CLIENT_ID}/goals")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_goal_not_found(client):
    with patch(
        "gym_api.routers.goals.goal_service.get_goal",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/goals/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_goal(client):
    goal = _make_goal()
    updated = _make_goal(current_value=80.0)
    with (
        patch("gym_api.routers.goals.goal_service.get_goal", new_callable=AsyncMock) as get_mock,
        patch("gym_api.routers.goals.goal_service.update_goal", new_callable=AsyncMock) as upd_mock,
    ):
        get_mock.return_value = goal
        upd_mock.return_value = updated
        resp = await client.put(
            f"/v1/goals/{GOAL_ID}",
            json={"current_value": 80.0},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["current_value"] == 80.0


@pytest.mark.asyncio
async def test_delete_goal(client):
    goal = _make_goal()
    with (
        patch("gym_api.routers.goals.goal_service.get_goal", new_callable=AsyncMock) as get_mock,
        patch("gym_api.routers.goals.goal_service.delete_goal", new_callable=AsyncMock) as del_mock,
    ):
        get_mock.return_value = goal
        del_mock.return_value = None
        resp = await client.delete(f"/v1/goals/{GOAL_ID}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_assign_program(client):
    cp = _make_client_program()
    with patch(
        "gym_api.routers.goals.client_program_service.assign_program",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = cp
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/programs",
            json={"program_id": str(PROGRAM_ID)},
        )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_program_days(client):
    days = [_make_program_day(), _make_program_day(name="Day 2 - Pull", order_index=1)]
    with patch(
        "gym_api.routers.goals.client_program_service.list_program_days",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = days
        resp = await client.get(f"/v1/programs/{PROGRAM_ID}/days")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_create_program_day_exercise(client):
    exercise = _make_day_exercise()
    with patch(
        "gym_api.routers.goals.client_program_service.create_program_day_exercise",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = exercise
        resp = await client.post(
            f"/v1/program-days/{DAY_ID}/exercises",
            json={
                "exercise_id": str(uuid.uuid4()),
                "order_index": 0,
                "default_sets": 3,
                "default_reps": 10,
            },
        )
    assert resp.status_code == 201
