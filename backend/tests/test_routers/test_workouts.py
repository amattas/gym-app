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


def _make_workout(**overrides):
    defaults = dict(
        workout_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        trainer_id=None,
        program_id=None,
        status="scheduled",
        started_at=None,
        ended_at=None,
        notes=None,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_workout_exercise(**overrides):
    defaults = dict(
        workout_exercise_id=uuid.uuid4(),
        workout_id=uuid.uuid4(),
        exercise_id=uuid.uuid4(),
        order_index=0,
        target_sets=3,
        target_reps=10,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_workout_set(**overrides):
    defaults = dict(
        set_id=uuid.uuid4(),
        workout_exercise_id=uuid.uuid4(),
        set_index=0,
        weight_kg=60.0,
        reps=10,
        duration_seconds=None,
        completed=True,
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
async def test_create_workout(client):
    w = _make_workout()
    with patch(
        "gym_api.routers.workouts.workout_service.create_workout", new_callable=AsyncMock
    ) as mock:
        mock.return_value = w
        resp = await client.post(
            "/v1/workouts",
            json={"client_id": str(CLIENT_ID)},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "scheduled"


@pytest.mark.asyncio
async def test_list_workouts(client):
    workouts = [_make_workout(), _make_workout(status="completed")]
    with patch(
        "gym_api.routers.workouts.workout_service.list_workouts", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (workouts, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/workouts")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_list_workouts_filter_client(client):
    w = _make_workout()
    with patch(
        "gym_api.routers.workouts.workout_service.list_workouts", new_callable=AsyncMock
    ) as mock:
        mock.return_value = ([w], {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/workouts?client_id={CLIENT_ID}")
    assert resp.status_code == 200
    mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_workout(client):
    w = _make_workout()
    with patch(
        "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
    ) as mock:
        mock.return_value = w
        resp = await client.get(f"/v1/workouts/{w.workout_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_workout(client):
    w = _make_workout()
    updated = _make_workout(status="in_progress")
    with (
        patch(
            "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.workouts.workout_service.update_workout", new_callable=AsyncMock
        ) as upd_mock,
    ):
        get_mock.return_value = w
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/workouts/{w.workout_id}",
            json={"status": "in_progress"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_add_exercise_to_workout(client):
    w = _make_workout()
    we = _make_workout_exercise(workout_id=w.workout_id)
    with (
        patch(
            "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.workouts.workout_service.add_exercise_to_workout",
            new_callable=AsyncMock,
        ) as add_mock,
    ):
        get_mock.return_value = w
        add_mock.return_value = we
        resp = await client.post(
            f"/v1/workouts/{w.workout_id}/exercises",
            json={"exercise_id": str(we.exercise_id), "order_index": 0},
        )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_workout_exercises(client):
    w = _make_workout()
    exercises = [_make_workout_exercise(workout_id=w.workout_id)]
    with (
        patch(
            "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.workouts.workout_service.list_workout_exercises",
            new_callable=AsyncMock,
        ) as list_mock,
    ):
        get_mock.return_value = w
        list_mock.return_value = exercises
        resp = await client.get(f"/v1/workouts/{w.workout_id}/exercises")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_add_set(client):
    w = _make_workout()
    we = _make_workout_exercise(workout_id=w.workout_id)
    ws = _make_workout_set(workout_exercise_id=we.workout_exercise_id)
    with (
        patch(
            "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.workouts.workout_service.add_set", new_callable=AsyncMock
        ) as add_mock,
    ):
        get_mock.return_value = w
        add_mock.return_value = ws
        resp = await client.post(
            f"/v1/workouts/{w.workout_id}/exercises/{we.workout_exercise_id}/sets",
            json={"set_index": 0, "weight_kg": 60.0, "reps": 10},
        )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_sets(client):
    w = _make_workout()
    we_id = uuid.uuid4()
    sets = [_make_workout_set(workout_exercise_id=we_id)]
    with (
        patch(
            "gym_api.routers.workouts.workout_service.get_workout", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.workouts.workout_service.list_sets", new_callable=AsyncMock
        ) as list_mock,
    ):
        get_mock.return_value = w
        list_mock.return_value = sets
        resp = await client.get(f"/v1/workouts/{w.workout_id}/exercises/{we_id}/sets")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
