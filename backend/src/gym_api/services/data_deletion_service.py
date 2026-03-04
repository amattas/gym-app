import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client import Client
from gym_api.models.client_membership import ClientMembership, MembershipStatus
from gym_api.models.data_request import DeletionRequest, DeletionStatus
from gym_api.models.goal import ClientGoal, GoalStatus
from gym_api.models.measurement import Measurement
from gym_api.models.note import Note
from gym_api.models.progress_photo import ProgressPhoto


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


async def cancel_deletion_request(
    db: AsyncSession, deletion_id: uuid.UUID
) -> DeletionRequest | None:
    request = await get_deletion_request(db, deletion_id)
    if not request or request.status not in (DeletionStatus.pending, DeletionStatus.approved):
        return request
    request.status = DeletionStatus.rejected
    await db.commit()
    await db.refresh(request)
    return request


async def process_pending_deletions(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(DeletionRequest).where(
            DeletionRequest.status.in_([DeletionStatus.pending, DeletionStatus.approved]),
            DeletionRequest.scheduled_for <= now,
        )
    )
    requests = result.scalars().all()
    count = 0
    for req in requests:
        req.status = DeletionStatus.processing
        await db.commit()
        try:
            await _anonymize_client_data(db, req.client_id)
            req.status = DeletionStatus.completed
            req.completed_at = now
            count += 1
        except Exception:
            req.status = DeletionStatus.pending
        await db.commit()
    return count


async def _anonymize_client_data(db: AsyncSession, client_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Client).where(Client.client_id == client_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        return

    anon = f"deleted-{str(client_id)[:8]}"
    client.first_name = "Deleted"
    client.last_name = "User"
    client.email = f"{anon}@deleted.local"
    if hasattr(client, "phone"):
        client.phone = None

    await db.execute(
        update(ClientMembership)
        .where(ClientMembership.client_id == client_id)
        .values(status=MembershipStatus.cancelled)
    )

    await db.execute(
        update(ClientGoal)
        .where(ClientGoal.client_id == client_id)
        .values(status=GoalStatus.abandoned)
    )

    result = await db.execute(
        select(Note).where(Note.notable_type == "client", Note.notable_id == str(client_id))
    )
    for note in result.scalars().all():
        note.content = "[deleted]"

    result = await db.execute(
        select(ProgressPhoto).where(ProgressPhoto.client_id == client_id)
    )
    for photo in result.scalars().all():
        await db.delete(photo)

    result = await db.execute(
        select(Measurement).where(Measurement.client_id == client_id)
    )
    for m in result.scalars().all():
        await db.delete(m)

    await db.commit()
