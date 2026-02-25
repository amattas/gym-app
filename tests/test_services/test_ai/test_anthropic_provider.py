import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.ai.anthropic_provider import AnthropicProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


def _make_context() -> WorkoutSummaryContext:
    return WorkoutSummaryContext(
        client_name="Jane Smith",
        program_name="Upper/Lower Split",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=50,
                exercises=[
                    {"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 135},
                    {"name": "Bent Over Row", "sets": 3, "reps": 8, "weight_lbs": 115},
                ],
                total_volume_lbs=6000.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 22, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[
                    {"name": "Back Squat", "sets": 4, "reps": 5, "weight_lbs": 185},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": 10, "weight_lbs": 135},
                ],
                total_volume_lbs=7750.0,
                completion_rate=0.85,
                prs_achieved=1,
            ),
        ],
    )


@pytest.mark.asyncio
async def test_anthropic_provider_calls_api_and_returns_result():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Jane has been training consistently...")]
    mock_response.usage.input_tokens = 800
    mock_response.usage.output_tokens = 250

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    provider = AnthropicProvider(api_key="test-key", model="claude-sonnet-4-20250514")
    provider._client = mock_client

    result = await provider.generate_summary(_make_context())

    assert result.summary_text == "Jane has been training consistently..."
    assert result.prompt_tokens == 800
    assert result.completion_tokens == 250
    mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_anthropic_provider_passes_model_to_api():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Summary text")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    provider = AnthropicProvider(api_key="test-key", model="claude-haiku-4-5-20251001")
    provider._client = mock_client

    await provider.generate_summary(_make_context())

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
