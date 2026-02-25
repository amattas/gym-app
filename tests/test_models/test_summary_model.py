import uuid
from datetime import datetime, timezone

from gym_api.models.summary import ClientWorkoutSummary


def test_client_workout_summary_has_required_fields():
    summary = ClientWorkoutSummary(
        summary_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        gym_id=uuid.uuid4(),
        summary_text="Over the last 4 sessions, the client focused on...",
        workouts_included=[uuid.uuid4(), uuid.uuid4()],
        generated_at=datetime.now(timezone.utc),
        model_provider="anthropic",
        model_id="claude-sonnet-4-20250514",
        token_usage={"prompt_tokens": 1200, "completion_tokens": 350},
    )
    assert summary.summary_text.startswith("Over the last")
    assert summary.model_provider == "anthropic"
    assert len(summary.workouts_included) == 2
    assert summary.token_usage["prompt_tokens"] == 1200
