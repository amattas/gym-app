import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.schedule import (
    Schedule,
    ScheduleStatus,
    TrainerAvailability,
    TrainerException,
)
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_schedule(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Schedule:
    trainer_id = kwargs.get("trainer_id")
    start = kwargs.get("scheduled_start")
    end = kwargs.get("scheduled_end")
    if trainer_id and start and end:
        conflict = await _check_double_booking(db, trainer_id, start, end)
        if conflict:
            raise ValueError("Trainer has a conflicting schedule at this time")
    schedule = Schedule(gym_id=gym_id, **kwargs)
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def get_schedule(
    db: AsyncSession, gym_id: uuid.UUID, schedule_id: uuid.UUID
) -> Schedule | None:
    result = await db.execute(
        select(Schedule).where(
            Schedule.schedule_id == schedule_id,
            Schedule.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_schedules(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    trainer_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    date: datetime | None = None,
    status: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Schedule], dict]:
    query = select(Schedule).where(Schedule.gym_id == gym_id)
    if trainer_id:
        query = query.where(Schedule.trainer_id == trainer_id)
    if client_id:
        query = query.where(Schedule.client_id == client_id)
    if date:
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        query = query.where(
            Schedule.scheduled_start >= day_start, Schedule.scheduled_start < day_end
        )
    if status:
        query = query.where(Schedule.status == status)
    query = apply_cursor_pagination(
        query, order_column=Schedule.scheduled_start, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "scheduled_start")
    return items, pagination


async def update_schedule(db: AsyncSession, schedule: Schedule, **kwargs) -> Schedule:
    for key, value in kwargs.items():
        if value is not None:
            setattr(schedule, key, value)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def update_schedule_status(
    db: AsyncSession, schedule: Schedule, *, status: ScheduleStatus
) -> Schedule:
    schedule.status = status
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def get_trainer_availability(
    db: AsyncSession, trainer_id: uuid.UUID
) -> list[TrainerAvailability]:
    result = await db.execute(
        select(TrainerAvailability)
        .where(TrainerAvailability.trainer_id == trainer_id)
        .order_by(TrainerAvailability.day_of_week, TrainerAvailability.start_time)
    )
    return list(result.scalars().all())


async def set_trainer_availability(
    db: AsyncSession, trainer_id: uuid.UUID, entries: list[dict]
) -> list[TrainerAvailability]:
    existing = await db.execute(
        select(TrainerAvailability).where(TrainerAvailability.trainer_id == trainer_id)
    )
    for row in existing.scalars().all():
        await db.delete(row)

    new_entries = []
    for entry in entries:
        avail = TrainerAvailability(trainer_id=trainer_id, **entry)
        db.add(avail)
        new_entries.append(avail)
    await db.commit()
    for entry in new_entries:
        await db.refresh(entry)
    return new_entries


async def create_trainer_exception(
    db: AsyncSession, *, trainer_id: uuid.UUID, **kwargs
) -> TrainerException:
    exc = TrainerException(trainer_id=trainer_id, **kwargs)
    db.add(exc)
    await db.commit()
    await db.refresh(exc)
    return exc


async def delete_trainer_exception(db: AsyncSession, exception: TrainerException) -> None:
    await db.delete(exception)
    await db.commit()


async def get_trainer_exception(
    db: AsyncSession, exception_id: uuid.UUID
) -> TrainerException | None:
    result = await db.execute(
        select(TrainerException).where(
            TrainerException.trainer_exception_id == exception_id
        )
    )
    return result.scalar_one_or_none()


async def _check_double_booking(
    db: AsyncSession,
    trainer_id: uuid.UUID,
    start: datetime,
    end: datetime,
    exclude_schedule_id: uuid.UUID | None = None,
) -> bool:
    query = select(Schedule).where(
        Schedule.trainer_id == trainer_id,
        Schedule.status.in_([ScheduleStatus.tentative, ScheduleStatus.confirmed]),
        Schedule.scheduled_start < end,
        Schedule.scheduled_end > start,
    )
    if exclude_schedule_id:
        query = query.where(Schedule.schedule_id != exclude_schedule_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None
