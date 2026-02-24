import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from gym_api.main import app
from gym_api.database import get_db


@pytest.fixture
def client_id():
    return uuid.uuid4()


@pytest.fixture
def gym_id():
    return uuid.uuid4()


def _mock_client(client_id, gym_id):
    client = MagicMock()
    client.client_id = client_id
    client.gym_id = gym_id
    client.first_name = "Test"
    client.last_name = "Client"
    return client


def _mock_db_with_client(client_obj):
    """Create a mock db that returns the client on first execute call."""
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()

    client_result = MagicMock()
    client_result.scalar_one_or_none.return_value = client_obj
    mock_db.execute.return_value = client_result

    return mock_db


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

    mock_client = _mock_client(client_id, gym_id)
    mock_db = _mock_db_with_client(mock_client)

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=cached), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=cached.generated_at - timedelta(hours=1)):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["summary_text"] == "Cached summary"
        assert body["data"]["is_cached"] is True

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_404_when_no_workouts(client_id, gym_id):
    mock_client = _mock_client(client_id, gym_id)
    mock_db = _mock_db_with_client(mock_client)

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=None), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=None):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_404_when_client_not_in_gym(client_id, gym_id):
    wrong_gym_id = uuid.uuid4()
    mock_client = _mock_client(client_id, wrong_gym_id)
    mock_db = _mock_db_with_client(mock_client)

    app.dependency_overrides[get_db] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

    assert resp.status_code == 404
    assert "Client not found" in resp.json()["detail"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_404_when_client_not_found(client_id, gym_id):
    mock_db = _mock_db_with_client(None)

    app.dependency_overrides[get_db] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

    assert resp.status_code == 404

    app.dependency_overrides.clear()
