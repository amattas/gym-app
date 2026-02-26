import pytest


@pytest.mark.asyncio
async def test_stripe_webhook_receives_event(client):
    resp = await client.post(
        "/v1/webhooks/stripe",
        json={"type": "payment_intent.succeeded", "data": {"object": {}}},
    )
    assert resp.status_code == 200
    assert resp.json()["received"] is True


@pytest.mark.asyncio
async def test_stripe_webhook_unknown_event(client):
    resp = await client.post(
        "/v1/webhooks/stripe",
        json={"type": "unknown.event", "data": {}},
    )
    assert resp.status_code == 200
    assert resp.json()["received"] is True
