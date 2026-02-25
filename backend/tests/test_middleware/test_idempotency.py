import pytest
from fastapi import APIRouter

from gym_api.main import app

idem_router = APIRouter()

_call_count = 0


@idem_router.post("/test/idempotent")
async def idempotent_endpoint():
    global _call_count
    _call_count += 1
    return {"call_count": _call_count}


@idem_router.get("/test/idempotent-get")
async def idempotent_get():
    return {"method": "get"}


app.include_router(idem_router)


@pytest.mark.asyncio
async def test_post_without_key_not_cached(client):
    global _call_count
    _call_count = 0
    r1 = await client.post("/test/idempotent")
    r2 = await client.post("/test/idempotent")
    assert r1.json()["call_count"] == 1
    assert r2.json()["call_count"] == 2


@pytest.mark.asyncio
async def test_post_with_key_returns_cached(client):
    global _call_count
    _call_count = 100
    headers = {"X-Idempotency-Key": "unique-key-1"}
    r1 = await client.post("/test/idempotent", headers=headers)
    r2 = await client.post("/test/idempotent", headers=headers)
    assert r1.json()["call_count"] == 101
    assert r2.json()["call_count"] == 101
    assert r2.headers.get("X-Idempotent-Replayed") == "true"


@pytest.mark.asyncio
async def test_get_ignores_idempotency_key(client):
    headers = {"X-Idempotency-Key": "get-key"}
    r1 = await client.get("/test/idempotent-get", headers=headers)
    assert r1.json()["method"] == "get"
    assert r1.headers.get("X-Idempotent-Replayed") is None


@pytest.mark.asyncio
async def test_different_keys_not_shared(client):
    global _call_count
    _call_count = 200
    r1 = await client.post("/test/idempotent", headers={"X-Idempotency-Key": "key-a"})
    r2 = await client.post("/test/idempotent", headers={"X-Idempotency-Key": "key-b"})
    assert r1.json()["call_count"] == 201
    assert r2.json()["call_count"] == 202
