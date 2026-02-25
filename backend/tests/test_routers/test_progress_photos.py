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
PHOTO_ID = uuid.uuid4()
USER_ID = uuid.uuid4()


def _make_photo(**overrides):
    defaults = dict(
        photo_id=PHOTO_ID,
        gym_id=GYM_ID,
        client_id=CLIENT_ID,
        storage_key="photos/2026/03/front.jpg",
        content_type="image/jpeg",
        notes=None,
        tags=None,
        measurement_id=None,
        uploaded_by_user_id=USER_ID,
        captured_at=None,
        created_at=datetime.now(timezone.utc),
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
async def test_create_progress_photo(client):
    photo = _make_photo()
    with patch(
        "gym_api.routers.progress_photos.progress_photo_service.create_photo",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = photo
        resp = await client.post(
            f"/v1/clients/{CLIENT_ID}/progress-photos",
            json={"storage_key": "photos/2026/03/front.jpg", "content_type": "image/jpeg"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["storage_key"] == "photos/2026/03/front.jpg"


@pytest.mark.asyncio
async def test_list_progress_photos(client):
    photos = [_make_photo(), _make_photo(storage_key="photos/2026/03/side.jpg")]
    with patch(
        "gym_api.routers.progress_photos.progress_photo_service.list_client_photos",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (photos, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get(f"/v1/clients/{CLIENT_ID}/progress-photos")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_delete_progress_photo(client):
    photo = _make_photo()
    with (
        patch(
            "gym_api.routers.progress_photos.progress_photo_service.get_photo",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.progress_photos.progress_photo_service.delete_photo",
            new_callable=AsyncMock,
        ) as del_mock,
    ):
        get_mock.return_value = photo
        del_mock.return_value = None
        resp = await client.delete(f"/v1/progress-photos/{PHOTO_ID}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_progress_photo_not_found(client):
    with patch(
        "gym_api.routers.progress_photos.progress_photo_service.get_photo",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.delete(f"/v1/progress-photos/{uuid.uuid4()}")
    assert resp.status_code == 404
