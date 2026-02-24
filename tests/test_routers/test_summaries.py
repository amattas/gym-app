import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from gym_api.main import app


@pytest.fixture
def client_id():
    return uuid.uuid4()


@pytest.fixture
def gym_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_cached(client_id, gym_id):
    cached = MagicMock()
    cached.summary_id = uuid.uuid4()
    cached.client_id = client_id
    cached.gym_id = gym_id
    cached.summary_text = "Cached summary"
    cached.workouts_included = [uuid.uuid4()]
    cached.generated_at = datetime.now(timezone.utc)
    cached.model_provider = "anthropic"
    cached.model_id = "test"
    cached.token_usage = {"prompt_tokens": 100, "completion_tokens": 50}

    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=cached), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=cached.generated_at - timedelta(hours=1)), \
         patch("gym_api.routers.summaries.get_db") as mock_get_db:

        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        # Override the dependency
        app.dependency_overrides[__import__('gym_api.database', fromlist=['get_db']).get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["summary_text"] == "Cached summary"
        assert body["data"]["is_cached"] is True

        # Clean up dependency override
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_404_when_no_workouts(client_id, gym_id):
    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=None), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=None):

        mock_db = AsyncMock()
        from gym_api.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 404

        app.dependency_overrides.clear()
