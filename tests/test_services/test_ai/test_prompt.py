import uuid
from datetime import datetime, timezone

from gym_api.services.ai.prompt import build_summary_prompt, SYSTEM_PROMPT
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


def test_prompt_includes_client_name():
    ctx = WorkoutSummaryContext(
        client_name="Jane Smith",
        program_name="Push/Pull",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[{"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 135}],
                total_volume_lbs=3240.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
        ],
    )
    prompt = build_summary_prompt(ctx)
    assert "Jane Smith" in prompt
    assert "Push/Pull" in prompt
    assert "Bench Press" in prompt
    assert "3240" in prompt


def test_prompt_handles_no_program():
    ctx = WorkoutSummaryContext(
        client_name="John",
        program_name=None,
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=30,
                exercises=[],
                total_volume_lbs=0,
                completion_rate=0,
                prs_achieved=0,
            ),
        ],
    )
    prompt = build_summary_prompt(ctx)
    assert "John" in prompt
    assert "Program" not in prompt


def test_system_prompt_forbids_recommendations():
    assert "Do not give recommendations" in SYSTEM_PROMPT
