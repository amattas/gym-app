from unittest.mock import AsyncMock, patch

import httpx

from gym_api.webhooks.webhook_service import (
    deliver_webhook,
    sign_payload,
    verify_signature,
)


def test_sign_payload():
    payload = '{"event": "test"}'
    secret = "my_secret"
    sig = sign_payload(payload, secret)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest


def test_verify_signature_valid():
    payload = '{"event": "test"}'
    secret = "my_secret"
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret) is True


def test_verify_signature_invalid():
    payload = '{"event": "test"}'
    secret = "my_secret"
    assert verify_signature(payload, "invalid_signature", secret) is False


async def test_deliver_webhook_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await deliver_webhook(
            url="https://example.com/webhook",
            event="test.event",
            payload={"id": 1},
            secret="secret123",
        )
    assert result is True
    mock_client.post.assert_called_once()
    call_kwargs = mock_client.post.call_args
    assert "X-Webhook-Signature" in call_kwargs.kwargs.get(
        "headers", call_kwargs[1].get("headers", {})
    )


async def test_deliver_webhook_retries_on_failure():
    mock_response = AsyncMock()
    mock_response.status_code = 500

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await deliver_webhook(
            url="https://example.com/webhook",
            event="test.event",
            payload={"id": 1},
            secret="secret123",
        )
    assert result is False
    assert mock_client.post.call_count == 3


async def test_deliver_webhook_retries_on_request_error():
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(
        side_effect=httpx.RequestError("connection failed", request=None)
    )
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await deliver_webhook(
            url="https://example.com/webhook",
            event="test.event",
            payload={"id": 1},
            secret="secret123",
        )
    assert result is False
    assert mock_client.post.call_count == 3
