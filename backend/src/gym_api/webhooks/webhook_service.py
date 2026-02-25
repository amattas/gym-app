import hashlib
import hmac
import json
import logging
import time

import httpx

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [1, 5, 30]


def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)


async def deliver_webhook(
    *,
    url: str,
    event: str,
    payload: dict,
    secret: str,
) -> bool:
    body = json.dumps(
        {"event": event, "timestamp": int(time.time()), "data": payload},
        default=str,
    )
    signature = sign_payload(body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Event": event,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.post(url, content=body, headers=headers)
                if 200 <= resp.status_code < 300:
                    logger.info(
                        "Webhook delivered: url=%s event=%s status=%d",
                        url,
                        event,
                        resp.status_code,
                    )
                    return True
                logger.warning(
                    "Webhook failed: url=%s status=%d attempt=%d",
                    url,
                    resp.status_code,
                    attempt + 1,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "Webhook error: url=%s error=%s attempt=%d",
                    url,
                    str(e),
                    attempt + 1,
                )
            if attempt < MAX_RETRIES - 1:
                import asyncio

                await asyncio.sleep(RETRY_BACKOFF_SECONDS[attempt])

    logger.error("Webhook exhausted retries: url=%s event=%s", url, event)
    return False
