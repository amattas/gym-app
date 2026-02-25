import pytest


@pytest.mark.asyncio
async def test_rate_limit_headers_present(client):
    resp = await client.get("/health/live")
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers


@pytest.mark.asyncio
async def test_rate_limit_decrements(client):
    r1 = await client.get("/health/live")
    r2 = await client.get("/health/live")
    rem1 = int(r1.headers["X-RateLimit-Remaining"])
    rem2 = int(r2.headers["X-RateLimit-Remaining"])
    assert rem2 == rem1 - 1


@pytest.mark.asyncio
async def test_auth_endpoint_has_tighter_limit(client):
    resp = await client.post(
        "/v1/auth/login",
        json={"email": "a@b.com", "password": "x"},
    )
    assert resp.headers["X-RateLimit-Limit"] == "10"
