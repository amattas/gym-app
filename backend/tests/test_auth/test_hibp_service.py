from unittest.mock import AsyncMock, patch

import pytest

from gym_api.services.hibp_service import check_password_breach


@pytest.mark.asyncio
async def test_breached_password_detected():
    fake_response = AsyncMock()
    fake_response.status_code = 200
    fake_response.raise_for_status = lambda: None

    import hashlib

    sha1 = hashlib.sha1(b"password123").hexdigest().upper()
    suffix = sha1[5:]
    fake_response.text = f"{suffix}:5000\nABCDEF12345:1"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=fake_response)

    with patch("gym_api.services.hibp_service.httpx.AsyncClient", return_value=mock_client):
        result = await check_password_breach("password123")
    assert result is True


@pytest.mark.asyncio
async def test_safe_password_not_flagged():
    fake_response = AsyncMock()
    fake_response.status_code = 200
    fake_response.raise_for_status = lambda: None
    fake_response.text = "ABCDEF12345:1\n1234567890A:2"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=fake_response)

    with patch("gym_api.services.hibp_service.httpx.AsyncClient", return_value=mock_client):
        result = await check_password_breach("super-unique-password-xyz-12345")
    assert result is False


@pytest.mark.asyncio
async def test_hibp_unavailable_fails_open():
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=ConnectionError("API down"))

    with patch("gym_api.services.hibp_service.httpx.AsyncClient", return_value=mock_client):
        result = await check_password_breach("any-password")
    assert result is False
