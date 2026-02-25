import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.data_request import DeletionRequest


async def create_deletion_request(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    reason: str | None = None,
    grace_period_days: int = 30,
) -> DeletionRequest:
    request = DeletionRequest(
        gym_id=gym_id,
        client_id=client_id,
        reason=reason,
        scheduled_for=datetime.now(timezone.utc) + timedelta(days=grace_period_days),
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def get_deletion_request(
    db: AsyncSession, deletion_id: uuid.UUID
) -> DeletionRequest | None:
    result = await db.execute(
        select(DeletionRequest).where(DeletionRequest.deletion_id == deletion_id)
    )
    return result.scalar_one_or_none()
