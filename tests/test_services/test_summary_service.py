import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.summary_service import SummaryService
from gym_api.services.ai.types import SummaryResult


def _make_workout_row(client_id, ended_at, exercises=None):
    workout = MagicMock()
    workout.workout_id = uuid.uuid4()
    workout.client_id = client_id
    workout.started_at = ended_at - timedelta(minutes=50)
    workout.ended_at = ended_at
    workout.status = "completed"
    workout.program_id = None

    if exercises is None:
        ex = MagicMock()
        ex.exercise.name = "Back Squat"
        ex.status = "complete"
        ex.order_index = 0
        s = MagicMock()
        s.set_index = 1
        s.actual_reps = 5
        m = MagicMock()
        m.type = "weight"
        m.value = 225.0
        m.unit = "lbs"
        s.measurements = [m]
        ex.sets = [s]
        workout.exercises = [ex]
    else:
        workout.exercises = exercises

    return workout


def _make_analytics_row(workout_id):
    a = MagicMock()
    a.workout_id = workout_id
    a.total_weight_lifted_lbs = 3375.0
    a.total_reps = 15
    a.total_sets = 3
    a.duration_minutes = 50
    a.exercises_completed = 3
    a.exercises_skipped = 0
    a.completion_rate = 1.0
    a.prs_achieved_count = 0
    a.volume_by_muscle_group = {"legs": 3375.0}
    return a


@pytest.mark.asyncio
async def test_get_summary_generates_on_cache_miss():
    client_id = uuid.uuid4()
    gym_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    workouts = [_make_workout_row(client_id, now - timedelta(days=i)) for i in range(3)]
    analytics = {w.workout_id: _make_analytics_row(w.workout_id) for w in workouts}

    mock_provider = AsyncMock()
    mock_provider.generate_summary = AsyncMock(
        return_value=SummaryResult(
            summary_text="Client has been consistent...",
            prompt_tokens=1000,
            completion_tokens=300,
        )
    )

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = SummaryService(provider=mock_provider, provider_name="anthropic", model_id="test-model")
    result = await service.get_summary(
        db=mock_db,
        client_id=client_id,
        gym_id=gym_id,
        workouts=workouts,
        analytics=analytics,
        client_name="Test Client",
        program_name=None,
        cached_summary=None,
    )

    assert result.summary_text == "Client has been consistent..."
    mock_provider.generate_summary.assert_called_once()


@pytest.mark.asyncio
async def test_get_summary_returns_cache_when_valid():
    mock_provider = AsyncMock()

    cached = MagicMock()
    cached.summary_id = uuid.uuid4()
    cached.client_id = uuid.uuid4()
    cached.summary_text = "Cached summary text"
    cached.workouts_included = [uuid.uuid4()]
    cached.generated_at = datetime.now(timezone.utc)
    cached.model_provider = "anthropic"
    cached.model_id = "test-model"
    cached.token_usage = {"prompt_tokens": 500, "completion_tokens": 200}

    service = SummaryService(provider=mock_provider, provider_name="anthropic", model_id="test-model")
    result = await service.get_summary(
        db=AsyncMock(),
        client_id=cached.client_id,
        gym_id=uuid.uuid4(),
        workouts=[],
        analytics={},
        client_name="Test",
        program_name=None,
        cached_summary=cached,
    )

    assert result.summary_text == "Cached summary text"
    mock_provider.generate_summary.assert_not_called()
