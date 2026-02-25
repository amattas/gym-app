import uuid
from datetime import datetime, timezone

from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData, SummaryResult


def test_workout_summary_context_holds_client_and_workouts():
    ctx = WorkoutSummaryContext(
        client_name="John Doe",
        program_name="Beginner Strength",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=55,
                exercises=[{"name": "Back Squat", "sets": 3, "reps": 5, "weight_lbs": 225}],
                total_volume_lbs=3375.0,
                completion_rate=1.0,
                prs_achieved=1,
            ),
        ],
    )
    assert ctx.client_name == "John Doe"
    assert len(ctx.workouts) == 1
    assert ctx.workouts[0].total_volume_lbs == 3375.0


def test_summary_result_holds_text_and_usage():
    result = SummaryResult(
        summary_text="John has been consistent...",
        prompt_tokens=1200,
        completion_tokens=350,
    )
    assert result.summary_text.startswith("John")
    assert result.total_tokens == 1550
