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


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


def _make_workout():
    return SimpleNamespace(
        workout_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=uuid.uuid4(),
        status="completed",
    )


def _make_workout_exercise(workout_id):
    return SimpleNamespace(
        workout_exercise_id=uuid.uuid4(),
        workout_id=workout_id,
        exercise_id=uuid.uuid4(),
        order_index=0,
        target_sets=3,
        target_reps=10,
    )


def _make_set(we_id):
    return SimpleNamespace(
        set_id=uuid.uuid4(),
        workout_exercise_id=we_id,
        set_index=0,
        weight_kg=80.0,
        reps=10,
        duration_seconds=None,
        completed=True,
    )


@pytest.mark.asyncio
async def test_analytics_preview(client):
    w = _make_workout()
    we = _make_workout_exercise(w.workout_id)
    s = _make_set(we.workout_exercise_id)

    with (
        patch(
            "gym_api.routers.analytics.workout_service.get_workout",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.analytics.workout_service.list_workout_exercises",
            new_callable=AsyncMock,
        ) as ex_mock,
        patch(
            "gym_api.routers.analytics.workout_service.list_sets",
            new_callable=AsyncMock,
        ) as sets_mock,
    ):
        get_mock.return_value = w
        ex_mock.return_value = [we]
        sets_mock.return_value = [s]
        resp = await client.get(
            f"/v1/workouts/{w.workout_id}/analytics/preview"
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_volume_kg"] == 800.0
    assert data["total_sets"] == 1
    assert data["total_reps"] == 10


@pytest.mark.asyncio
async def test_analytics_preview_not_found(client):
    with patch(
        "gym_api.routers.analytics.workout_service.get_workout",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(
            f"/v1/workouts/{uuid.uuid4()}/analytics/preview"
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_personal_records(client):
    pr = SimpleNamespace(
        record_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=uuid.uuid4(),
        exercise_id=uuid.uuid4(),
        pr_type="1RM",
        weight_kg=100.0,
        reps=1,
        volume_kg=None,
        exercise_name="Bench Press",
        achieved_at=datetime.now(timezone.utc),
    )
    with patch(
        "gym_api.routers.analytics.pr_service.list_prs",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = [pr]
        resp = await client.get(
            f"/v1/clients/{pr.client_id}/personal-records"
        )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["pr_type"] == "1RM"
