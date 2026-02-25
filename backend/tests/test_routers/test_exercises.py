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


def _make_exercise(**overrides):
    defaults = dict(
        exercise_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="Bench Press",
        description="Flat barbell bench press",
        muscle_groups=["chest", "triceps"],
        equipment="Barbell",
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
async def test_create_exercise(client):
    e = _make_exercise()
    with patch(
        "gym_api.routers.exercises.exercise_service.create_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.post(
            "/v1/exercises",
            json={"name": "Bench Press", "muscle_groups": ["chest", "triceps"]},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Bench Press"


@pytest.mark.asyncio
async def test_list_exercises(client):
    exercises = [_make_exercise(), _make_exercise(name="Squat", gym_id=None)]
    with patch(
        "gym_api.routers.exercises.exercise_service.list_exercises", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (exercises, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/exercises")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_exercise(client):
    e = _make_exercise()
    with patch(
        "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.get(f"/v1/exercises/{e.exercise_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_exercise_cross_gym_denied(client):
    e = _make_exercise(gym_id=uuid.uuid4())  # different gym
    with patch(
        "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.get(f"/v1/exercises/{e.exercise_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_global_exercise_allowed(client):
    e = _make_exercise(gym_id=None)
    with patch(
        "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.get(f"/v1/exercises/{e.exercise_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_global_exercise_forbidden(client):
    e = _make_exercise(gym_id=None)
    with patch(
        "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.patch(
            f"/v1/exercises/{e.exercise_id}",
            json={"name": "Updated"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_exercise(client):
    e = _make_exercise()
    with (
        patch(
            "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.exercises.exercise_service.delete_exercise", new_callable=AsyncMock
        ),
    ):
        get_mock.return_value = e
        resp = await client.delete(f"/v1/exercises/{e.exercise_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_global_exercise_forbidden(client):
    e = _make_exercise(gym_id=None)
    with patch(
        "gym_api.routers.exercises.exercise_service.get_exercise", new_callable=AsyncMock
    ) as mock:
        mock.return_value = e
        resp = await client.delete(f"/v1/exercises/{e.exercise_id}")
    assert resp.status_code == 403
