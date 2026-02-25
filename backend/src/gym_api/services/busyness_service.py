import uuid
from datetime import datetime, timedelta

from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.check_in import GymCheckIn
from gym_api.models.schedule import Schedule, ScheduleStatus


async def get_location_busyness(
    db: AsyncSession,
    gym_id: uuid.UUID,
    location_id: uuid.UUID,
    date: datetime,
) -> list[dict]:
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    slots = []
    for i in range(96):
        slot_start = day_start + timedelta(minutes=15 * i)
        slot_end = slot_start + timedelta(minutes=15)

        checkin_count_result = await db.execute(
            select(sa_func.count()).where(
                GymCheckIn.gym_id == gym_id,
                GymCheckIn.location_id == location_id,
                GymCheckIn.checked_in_at < slot_end,
                GymCheckIn.checked_out_at.is_(None)
                | (GymCheckIn.checked_out_at > slot_start),
            )
        )
        checkin_count = checkin_count_result.scalar() or 0

        schedule_count_result = await db.execute(
            select(sa_func.count()).where(
                Schedule.gym_id == gym_id,
                Schedule.location_id == location_id,
                Schedule.status.in_([ScheduleStatus.tentative, ScheduleStatus.confirmed]),
                Schedule.scheduled_start < slot_end,
                Schedule.scheduled_end > slot_start,
            )
        )
        schedule_count = schedule_count_result.scalar() or 0

        slots.append({
            "time": slot_start.isoformat(),
            "check_ins": checkin_count,
            "scheduled": schedule_count,
            "total": checkin_count + schedule_count,
        })
    return slots


async def get_trainer_busyness(
    db: AsyncSession,
    trainer_id: uuid.UUID,
    date: datetime,
) -> list[dict]:
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(Schedule).where(
            Schedule.trainer_id == trainer_id,
            Schedule.status.in_([ScheduleStatus.tentative, ScheduleStatus.confirmed]),
            Schedule.scheduled_start >= day_start,
            Schedule.scheduled_start < day_end,
        ).order_by(Schedule.scheduled_start)
    )
    schedules = result.scalars().all()

    return [
        {
            "start": s.scheduled_start.isoformat(),
            "end": s.scheduled_end.isoformat(),
            "status": s.status.value if hasattr(s.status, "value") else s.status,
        }
        for s in schedules
    ]
