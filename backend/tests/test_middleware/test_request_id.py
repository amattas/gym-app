import uuid

import pytest


@pytest.mark.asyncio
async def test_generates_request_id(client):
    resp = await client.get("/health/live")
    rid = resp.headers.get("X-Request-ID")
    assert rid is not None
    uuid.UUID(rid)


@pytest.mark.asyncio
async def test_echoes_provided_request_id(client):
    custom_id = "my-custom-request-id-123"
    resp = await client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert resp.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_unique_ids_per_request(client):
    r1 = await client.get("/health/live")
    r2 = await client.get("/health/live")
    assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]
