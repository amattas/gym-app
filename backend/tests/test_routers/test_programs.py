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


def _make_program(**overrides):
    defaults = dict(
        program_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="Beginner Strength",
        description="4-week program",
        created_by_trainer_id=None,
        template_scope="personal",
        num_days=4,
        periodization_config=None,
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
async def test_create_program(client):
    p = _make_program()
    with patch(
        "gym_api.routers.programs.program_service.create_program", new_callable=AsyncMock
    ) as mock:
        mock.return_value = p
        resp = await client.post(
            "/v1/programs",
            json={"name": "Beginner Strength", "num_days": 4},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Beginner Strength"


@pytest.mark.asyncio
async def test_list_programs(client):
    programs = [_make_program(), _make_program(name="Advanced")]
    with patch(
        "gym_api.routers.programs.program_service.list_programs", new_callable=AsyncMock
    ) as mock:
        mock.return_value = (programs, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/programs")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_list_programs_filter_scope(client):
    p = _make_program(template_scope="gym_wide")
    with patch(
        "gym_api.routers.programs.program_service.list_programs", new_callable=AsyncMock
    ) as mock:
        mock.return_value = ([p], {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/programs?template_scope=gym_wide")
    assert resp.status_code == 200
    mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_program(client):
    p = _make_program()
    with patch(
        "gym_api.routers.programs.program_service.get_program", new_callable=AsyncMock
    ) as mock:
        mock.return_value = p
        resp = await client.get(f"/v1/programs/{p.program_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_program(client):
    p = _make_program()
    updated = _make_program(name="Updated Program")
    with (
        patch(
            "gym_api.routers.programs.program_service.get_program", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.programs.program_service.update_program", new_callable=AsyncMock
        ) as upd_mock,
    ):
        get_mock.return_value = p
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/programs/{p.program_id}",
            json={"name": "Updated Program"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Program"


@pytest.mark.asyncio
async def test_delete_program(client):
    p = _make_program()
    with (
        patch(
            "gym_api.routers.programs.program_service.get_program", new_callable=AsyncMock
        ) as get_mock,
        patch(
            "gym_api.routers.programs.program_service.delete_program", new_callable=AsyncMock
        ),
    ):
        get_mock.return_value = p
        resp = await client.delete(f"/v1/programs/{p.program_id}")
    assert resp.status_code == 204
