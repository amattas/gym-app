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
CLIENT_ID = uuid.uuid4()
WORKOUT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()


def _make_note(**overrides):
    defaults = dict(
        note_id=uuid.uuid4(),
        gym_id=GYM_ID,
        notable_type="client",
        notable_id=CLIENT_ID,
        author_user_id=USER_ID,
        content="Good progress this week",
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(user_id=USER_ID, role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_client_note(client):
    note = _make_note()
    with patch(
        "gym_api.routers.notes.note_service.create_note",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = note
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/notes",
            json={"content": "Good progress this week"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["content"] == "Good progress this week"


@pytest.mark.asyncio
async def test_list_client_notes(client):
    notes = [_make_note(), _make_note(content="Needs more flexibility work")]
    with patch(
        "gym_api.routers.notes.note_service.list_notes",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (notes, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/clients/{CLIENT_ID}/notes")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_create_workout_note(client):
    note = _make_note(notable_type="workout", notable_id=WORKOUT_ID)
    with patch(
        "gym_api.routers.notes.note_service.create_note",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = note
        resp = await client.post(
            f"/v1/workouts/{WORKOUT_ID}/notes",
            json={"content": "Great session"},
        )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_workout_notes(client):
    notes = [_make_note(notable_type="workout", notable_id=WORKOUT_ID)]
    with patch(
        "gym_api.routers.notes.note_service.list_notes",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (notes, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/workouts/{WORKOUT_ID}/notes")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
