import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.check_in import GymCheckIn
from gym_api.models.client_membership import ClientMembership, MembershipStatus
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta

logger = logging.getLogger(__name__)


async def create_check_in(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    location_id: uuid.UUID | None = None,
    schedule_id: uuid.UUID | None = None,
    check_in_method: str = "manual",
    checked_in_by_user_id: uuid.UUID | None = None,
) -> GymCheckIn:
    membership_result = await db.execute(
        select(sa_func.count()).where(
            ClientMembership.client_id == client_id,
            ClientMembership.gym_id == gym_id,
            ClientMembership.status == MembershipStatus.active,
        )
    )
    active_count = membership_result.scalar() or 0
    if active_count == 0:
        logger.warning(
            "Client %s has no active membership at gym %s",
            client_id,
            gym_id,
        )

    check_in = GymCheckIn(
        gym_id=gym_id,
        client_id=client_id,
        location_id=location_id,
        schedule_id=schedule_id,
        check_in_method=check_in_method,
        checked_in_by_user_id=checked_in_by_user_id,
    )
    db.add(check_in)
    await db.commit()
    await db.refresh(check_in)
    return check_in


async def get_check_in(
    db: AsyncSession, gym_id: uuid.UUID, check_in_id: uuid.UUID
) -> GymCheckIn | None:
    result = await db.execute(
        select(GymCheckIn).where(
            GymCheckIn.check_in_id == check_in_id,
            GymCheckIn.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_check_ins(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    location_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    date: datetime | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[GymCheckIn], dict]:
    query = select(GymCheckIn).where(GymCheckIn.gym_id == gym_id)
    if location_id:
        query = query.where(GymCheckIn.location_id == location_id)
    if client_id:
        query = query.where(GymCheckIn.client_id == client_id)
    if date:
        from datetime import timedelta

        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        query = query.where(
            GymCheckIn.checked_in_at >= day_start, GymCheckIn.checked_in_at < day_end
        )
    query = apply_cursor_pagination(
        query, order_column=GymCheckIn.checked_in_at, cursor=cursor, limit=limit,
        ascending=False,
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "checked_in_at")
    return items, pagination


async def checkout(db: AsyncSession, check_in: GymCheckIn) -> GymCheckIn:
    check_in.checked_out_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(check_in)
    return check_in


async def get_active_occupancy(
    db: AsyncSession, gym_id: uuid.UUID, location_id: uuid.UUID
) -> int:
    result = await db.execute(
        select(sa_func.count()).where(
            GymCheckIn.gym_id == gym_id,
            GymCheckIn.location_id == location_id,
            GymCheckIn.checked_out_at.is_(None),
        )
    )
    return result.scalar() or 0


async def get_occupancy_history(
    db: AsyncSession, *, location_id: uuid.UUID, date: datetime
) -> list[dict]:
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    results = []
    for hour in range(24):
        slot_start = day_start + timedelta(hours=hour)
        slot_end = slot_start + timedelta(hours=1)
        count_result = await db.execute(
            select(sa_func.count()).where(
                GymCheckIn.location_id == location_id,
                GymCheckIn.checked_in_at >= slot_start,
                GymCheckIn.checked_in_at < slot_end,
            )
        )
        count = count_result.scalar() or 0
        results.append({"hour": hour, "count": count})
    return results
