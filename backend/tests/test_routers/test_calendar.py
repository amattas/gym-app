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
TRAINER_ID = uuid.uuid4()
CLIENT_ID = uuid.uuid4()
TOKEN_ID = uuid.uuid4()


def _make_calendar_token(**overrides):
    defaults = dict(
        token_id=TOKEN_ID,
        gym_id=GYM_ID,
        owner_type="trainer",
        owner_id=TRAINER_ID,
        token_hash="hashed_token",
        is_revoked=False,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(role=UserRole.gym_admin, gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_location_busyness(client):
    with patch(
        "gym_api.routers.calendar.busyness_service.get_location_busyness",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = [{"time_slot": "09:00", "count": 5}]
        resp = await client.get(
            f"/v1/locations/{uuid.uuid4()}/busyness?date=2026-03-01T00:00:00Z"
        )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_trainer_busyness(client):
    with patch(
        "gym_api.routers.calendar.busyness_service.get_trainer_busyness",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = [{"time_slot": "10:00", "count": 2}]
        resp = await client.get(
            f"/v1/trainers/{TRAINER_ID}/busyness?date=2026-03-01T00:00:00Z"
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_generate_trainer_calendar_token(client):
    cal_token = _make_calendar_token()
    with patch(
        "gym_api.routers.calendar.ical_service.generate_token",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (cal_token, "raw_token_abc123")
        resp = await client.post(f"/v1/trainers/{TRAINER_ID}/calendar/token/generate")
    assert resp.status_code == 200
    assert resp.json()["data"]["token"] == "raw_token_abc123"


@pytest.mark.asyncio
async def test_get_trainer_ics_valid_token(client):
    cal_token = _make_calendar_token()
    with (
        patch(
            "gym_api.routers.calendar.ical_service.validate_token",
            new_callable=AsyncMock,
        ) as val_mock,
        patch(
            "gym_api.routers.calendar.ical_service.generate_ics",
            new_callable=AsyncMock,
        ) as ics_mock,
    ):
        val_mock.return_value = cal_token
        ics_mock.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"
        resp = await client.get(
            f"/v1/trainers/{TRAINER_ID}/calendar.ics?token=valid_token"
        )
    assert resp.status_code == 200
    assert "VCALENDAR" in resp.text


@pytest.mark.asyncio
async def test_get_trainer_ics_invalid_token(client):
    with patch(
        "gym_api.routers.calendar.ical_service.validate_token",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(
            f"/v1/trainers/{TRAINER_ID}/calendar.ics?token=bad_token"
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_generate_client_calendar_token(client):
    cal_token = _make_calendar_token(owner_type="client", owner_id=CLIENT_ID)
    with patch(
        "gym_api.routers.calendar.ical_service.generate_token",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (cal_token, "client_token_xyz")
        resp = await client.post(f"/v1/clients/{CLIENT_ID}/calendar/token/generate")
    assert resp.status_code == 200
    assert resp.json()["data"]["token"] == "client_token_xyz"


@pytest.mark.asyncio
async def test_get_dashboard(client):
    with patch(
        "gym_api.routers.calendar.reporting_service.get_gym_dashboard",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {"total_clients": 100, "active_memberships": 80}
        resp = await client.get(f"/v1/gyms/{GYM_ID}/analytics/dashboard")
    assert resp.status_code == 200
    assert resp.json()["data"]["total_clients"] == 100


@pytest.mark.asyncio
async def test_get_trainer_analytics(client):
    with patch(
        "gym_api.routers.calendar.reporting_service.get_trainer_utilization",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = [{"trainer_id": str(TRAINER_ID), "sessions": 20}]
        resp = await client.get(
            f"/v1/gyms/{GYM_ID}/analytics/trainers"
            "?start_date=2026-01-01T00:00:00Z&end_date=2026-03-01T00:00:00Z"
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_client_adherence(client):
    with patch(
        "gym_api.routers.calendar.reporting_service.get_client_adherence",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {"scheduled": 10, "completed": 8, "adherence_rate": 0.8}
        resp = await client.get(
            f"/v1/clients/{CLIENT_ID}/adherence"
            "?start_date=2026-01-01T00:00:00Z&end_date=2026-03-01T00:00:00Z"
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["adherence_rate"] == 0.8
