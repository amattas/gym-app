import pytest


@pytest.mark.asyncio
async def test_security_headers_present(client):
    resp = await client.get("/health/live")
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-XSS-Protection"] == "1; mode=block"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "geolocation=()" in resp.headers["Permissions-Policy"]
    assert "max-age=31536000" in resp.headers["Strict-Transport-Security"]
    assert resp.headers["Cache-Control"] == "no-store"


@pytest.mark.asyncio
async def test_security_headers_on_error(client):
    resp = await client.get("/nonexistent-path")
    assert resp.headers["X-Frame-Options"] == "DENY"
