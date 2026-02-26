import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_template(**overrides):
    defaults = dict(
        agreement_template_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="Liability Waiver",
        description="Standard liability waiver",
        content="I agree to the terms...",
        is_active=True,
        requires_signature=True,
        metadata=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_envelope(**overrides):
    defaults = dict(
        envelope_id=uuid.uuid4(),
        gym_id=GYM_ID,
        template_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        status="sent",
        signer_email="client@example.com",
        signer_name="Jane Doe",
        external_envelope_id=None,
        provider="internal",
        signed_at=None,
        expires_at=None,
        signed_document_url=None,
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
async def test_create_agreement_template(client):
    t = _make_template()
    with patch(
        "gym_api.routers.agreements.esign_service.create_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = t
        resp = await client.post(
            "/v1/agreements/templates",
            json={
                "name": "Liability Waiver",
                "content": "I agree to the terms...",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Liability Waiver"


@pytest.mark.asyncio
async def test_list_agreement_templates(client):
    templates = [_make_template()]
    with patch(
        "gym_api.routers.agreements.esign_service.list_templates",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (
            templates,
            {"next_cursor": None, "has_more": False, "limit": 20},
        )
        resp = await client.get("/v1/agreements/templates")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_agreement_template(client):
    t = _make_template()
    with patch(
        "gym_api.routers.agreements.esign_service.get_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = t
        resp = await client.get(
            f"/v1/agreements/templates/{t.agreement_template_id}"
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_agreement_template_not_found(client):
    with patch(
        "gym_api.routers.agreements.esign_service.get_template",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(
            f"/v1/agreements/templates/{uuid.uuid4()}"
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_agreement_template(client):
    t = _make_template()
    updated = _make_template(name="Updated Waiver")
    with (
        patch(
            "gym_api.routers.agreements.esign_service.get_template",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.agreements.esign_service.update_template",
            new_callable=AsyncMock,
        ) as upd_mock,
    ):
        get_mock.return_value = t
        upd_mock.return_value = updated
        resp = await client.patch(
            f"/v1/agreements/templates/{t.agreement_template_id}",
            json={"name": "Updated Waiver"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Waiver"


@pytest.mark.asyncio
async def test_delete_agreement_template(client):
    t = _make_template()
    with (
        patch(
            "gym_api.routers.agreements.esign_service.get_template",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.agreements.esign_service.delete_template",
            new_callable=AsyncMock,
        ),
    ):
        get_mock.return_value = t
        resp = await client.delete(
            f"/v1/agreements/templates/{t.agreement_template_id}"
        )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_send_agreement(client):
    env = _make_envelope()
    with patch(
        "gym_api.routers.agreements.esign_service.send_envelope",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = env
        resp = await client.post(
            "/v1/agreements/send",
            json={
                "template_id": str(uuid.uuid4()),
                "client_id": str(uuid.uuid4()),
                "signer_email": "client@example.com",
                "signer_name": "Jane Doe",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "sent"


@pytest.mark.asyncio
async def test_list_envelopes(client):
    envelopes = [_make_envelope()]
    with patch(
        "gym_api.routers.agreements.esign_service.list_envelopes",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (
            envelopes,
            {"next_cursor": None, "has_more": False, "limit": 20},
        )
        resp = await client.get("/v1/agreements/envelopes")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_envelope(client):
    env = _make_envelope()
    with patch(
        "gym_api.routers.agreements.esign_service.get_envelope",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = env
        resp = await client.get(f"/v1/agreements/envelopes/{env.envelope_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_envelope_not_found(client):
    with patch(
        "gym_api.routers.agreements.esign_service.get_envelope",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(
            f"/v1/agreements/envelopes/{uuid.uuid4()}"
        )
    assert resp.status_code == 404
