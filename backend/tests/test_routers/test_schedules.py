import uuid
from datetime import datetime, time, timezone
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
SCHEDULE_ID = uuid.uuid4()


def _make_schedule(**overrides):
    defaults = dict(
        schedule_id=SCHEDULE_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        trainer_id=TRAINER_ID,
        location_id=None,
        scheduled_start=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        scheduled_end=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
        status="tentative",
        notes=None,
        created_by_user_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_availability(**overrides):
    defaults = dict(
        trainer_id=TRAINER_ID,
        day_of_week=1,
        location_id=None,
        start_time=time(9, 0),
        end_time=time(17, 0),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_exception(**overrides):
    defaults = dict(
        trainer_exception_id=uuid.uuid4(),
        trainer_id=TRAINER_ID,
        exception_date=datetime(2026, 3, 15, tzinfo=timezone.utc),
        exception_type="day_off",
        reason="Vacation",
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
async def test_create_schedule(client):
    sched = _make_schedule()
    with patch(
        "gym_api.routers.schedules.schedule_service.create_schedule",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = sched
        resp = await client.post(
            "/v1/schedules",
            json={
                "client_id": str(CLIENT_ID),
                "trainer_id": str(TRAINER_ID),
                "scheduled_start": "2026-03-01T10:00:00Z",
                "scheduled_end": "2026-03-01T11:00:00Z",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "tentative"


@pytest.mark.asyncio
async def test_create_schedule_conflict(client):
    with patch(
        "gym_api.routers.schedules.schedule_service.create_schedule",
        new_callable=AsyncMock,
    ) as mock:
        mock.side_effect = ValueError("Double-booking detected")
        resp = await client.post(
            "/v1/schedules",
            json={
                "client_id": str(CLIENT_ID),
                "trainer_id": str(TRAINER_ID),
                "scheduled_start": "2026-03-01T10:00:00Z",
                "scheduled_end": "2026-03-01T11:00:00Z",
            },
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_schedules(client):
    schedules = [_make_schedule(), _make_schedule(status="confirmed")]
    with patch(
        "gym_api.routers.schedules.schedule_service.list_schedules",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (schedules, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/schedules")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_schedule_not_found(client):
    with patch(
        "gym_api.routers.schedules.schedule_service.get_schedule",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/schedules/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_confirm_schedule(client):
    sched = _make_schedule()
    confirmed = _make_schedule(status="confirmed")
    with (
        patch(
            "gym_api.routers.schedules.schedule_service.get_schedule",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.schedules.schedule_service.update_schedule_status",
            new_callable=AsyncMock,
        ) as status_mock,
    ):
        get_mock.return_value = sched
        status_mock.return_value = confirmed
        resp = await client.post(f"/v1/schedules/{SCHEDULE_ID}/confirm")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "confirmed"


@pytest.mark.asyncio
async def test_cancel_schedule(client):
    sched = _make_schedule()
    cancelled = _make_schedule(status="canceled")
    with (
        patch(
            "gym_api.routers.schedules.schedule_service.get_schedule",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.schedules.schedule_service.update_schedule_status",
            new_callable=AsyncMock,
        ) as status_mock,
    ):
        get_mock.return_value = sched
        status_mock.return_value = cancelled
        resp = await client.post(f"/v1/schedules/{SCHEDULE_ID}/cancel")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "canceled"


@pytest.mark.asyncio
async def test_get_trainer_availability(client):
    entries = [_make_availability(), _make_availability(day_of_week=2)]
    with patch(
        "gym_api.routers.schedules.schedule_service.get_trainer_availability",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = entries
        resp = await client.get(f"/v1/trainers/{TRAINER_ID}/availability")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_create_trainer_exception(client):
    exc = _make_exception()
    with patch(
        "gym_api.routers.schedules.schedule_service.create_trainer_exception",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = exc
        resp = await client.post(
            f"/v1/trainers/{TRAINER_ID}/exceptions",
            json={
                "exception_date": "2026-03-15T00:00:00Z",
                "exception_type": "day_off",
                "reason": "Vacation",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["exception_type"] == "day_off"


@pytest.mark.asyncio
async def test_delete_trainer_exception_not_found(client):
    with patch(
        "gym_api.routers.schedules.schedule_service.get_trainer_exception",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.delete(f"/v1/trainer-exceptions/{uuid.uuid4()}")
    assert resp.status_code == 404
