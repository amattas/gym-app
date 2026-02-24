import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.ai.openai_provider import OpenAIProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


@pytest.mark.asyncio
async def test_openai_provider_calls_api_and_returns_result():
    ctx = WorkoutSummaryContext(
        client_name="John Doe",
        program_name="Push/Pull",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[{"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 185}],
                total_volume_lbs=4440.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
        ],
    )

    mock_choice = MagicMock()
    mock_choice.message.content = "John completed one session..."

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 900
    mock_response.usage.completion_tokens = 200

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    provider = OpenAIProvider(api_key="test-key", model="gpt-4o")
    provider._client = mock_client

    result = await provider.generate_summary(ctx)

    assert result.summary_text == "John completed one session..."
    assert result.prompt_tokens == 900
    assert result.completion_tokens == 200
