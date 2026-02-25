import pytest
from fastapi import APIRouter, HTTPException

from gym_api.main import app

error_router = APIRouter()


@error_router.get("/test/http-error")
async def raise_http_error():
    raise HTTPException(status_code=404, detail="Thing not found")


@error_router.get("/test/unhandled-error")
async def raise_unhandled():
    raise RuntimeError("boom")


@error_router.get("/test/validation/{item_id}")
async def validate_item(item_id: int):
    return {"item_id": item_id}


app.include_router(error_router)


@pytest.mark.asyncio
async def test_http_exception_format(client):
    resp = await client.get("/test/http-error")
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "HTTP_404"
    assert body["error"]["message"] == "Thing not found"
    assert "request_id" in body["meta"]


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500(client):
    resp = await client.get("/test/unhandled-error")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "request_id" in body["meta"]


@pytest.mark.asyncio
async def test_validation_error_format(client):
    resp = await client.get("/test/validation/not-a-number")
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert len(body["error"]["details"]) > 0
    assert "request_id" in body["meta"]


@pytest.mark.asyncio
async def test_error_includes_request_id_from_header(client):
    resp = await client.get(
        "/test/http-error", headers={"X-Request-ID": "err-test-123"}
    )
    body = resp.json()
    assert body["meta"]["request_id"] == "err-test-123"
