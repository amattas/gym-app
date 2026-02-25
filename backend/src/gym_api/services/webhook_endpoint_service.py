import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.webhook_endpoint import WebhookEndpoint


async def create_webhook(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> WebhookEndpoint:
    if "secret" not in kwargs or not kwargs["secret"]:
        kwargs["secret"] = secrets.token_urlsafe(32)
    webhook = WebhookEndpoint(gym_id=gym_id, **kwargs)
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook


async def get_webhook(
    db: AsyncSession, gym_id: uuid.UUID, webhook_id: uuid.UUID
) -> WebhookEndpoint | None:
    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.webhook_endpoint_id == webhook_id,
            WebhookEndpoint.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_webhooks(
    db: AsyncSession, gym_id: uuid.UUID
) -> list[WebhookEndpoint]:
    result = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.gym_id == gym_id)
    )
    return list(result.scalars().all())


async def update_webhook(
    db: AsyncSession, webhook: WebhookEndpoint, **kwargs
) -> WebhookEndpoint:
    for key, value in kwargs.items():
        if value is not None:
            setattr(webhook, key, value)
    await db.commit()
    await db.refresh(webhook)
    return webhook


async def delete_webhook(db: AsyncSession, webhook: WebhookEndpoint) -> None:
    await db.delete(webhook)
    await db.commit()
