import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_domain(**overrides):
    defaults = dict(
        domain_id=uuid.uuid4(),
        gym_id=GYM_ID,
        domain="mail.mygym.com",
        domain_type="email",
        status="pending",
        dns_records={"records": [{"type": "TXT", "name": "mail.mygym.com", "value": "v=spf1..."}]},
        verified_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_domain(client):
    d = _make_domain()
    with patch(
        "gym_api.routers.custom_domains.custom_domain_service.create_domain",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = d
        resp = await client.post(
            "/v1/domains",
            json={"domain": "mail.mygym.com", "domain_type": "email"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["domain"] == "mail.mygym.com"


@pytest.mark.asyncio
async def test_list_domains(client):
    domains = [_make_domain()]
    with patch(
        "gym_api.routers.custom_domains.custom_domain_service.list_domains",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = domains
        resp = await client.get("/v1/domains")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_domain(client):
    d = _make_domain()
    with patch(
        "gym_api.routers.custom_domains.custom_domain_service.get_domain",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = d
        resp = await client.get(f"/v1/domains/{d.domain_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_domain_not_found(client):
    with patch(
        "gym_api.routers.custom_domains.custom_domain_service.get_domain",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/domains/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_verify_domain(client):
    d = _make_domain()
    verified = _make_domain(status="verifying")
    with (
        patch(
            "gym_api.routers.custom_domains.custom_domain_service.get_domain",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.custom_domains.custom_domain_service.verify_domain",
            new_callable=AsyncMock,
        ) as verify_mock,
    ):
        get_mock.return_value = d
        verify_mock.return_value = verified
        resp = await client.post(f"/v1/domains/{d.domain_id}/verify")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "verifying"


@pytest.mark.asyncio
async def test_delete_domain(client):
    d = _make_domain()
    with (
        patch(
            "gym_api.routers.custom_domains.custom_domain_service.get_domain",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.custom_domains.custom_domain_service.delete_domain",
            new_callable=AsyncMock,
        ),
    ):
        get_mock.return_value = d
        resp = await client.delete(f"/v1/domains/{d.domain_id}")
    assert resp.status_code == 204
