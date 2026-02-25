import uuid
from datetime import datetime, timedelta

from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.check_in import GymCheckIn
from gym_api.models.client_membership import ClientMembership, MembershipStatus
from gym_api.models.schedule import Schedule, ScheduleStatus
from gym_api.models.workout import Workout, WorkoutStatus


async def get_gym_dashboard(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    period_days: int = 30,
) -> dict:
    now = datetime.utcnow()
    start = now - timedelta(days=period_days)

    active_members_result = await db.execute(
        select(sa_func.count()).where(
            ClientMembership.gym_id == gym_id,
            ClientMembership.status == MembershipStatus.active,
        )
    )
    active_members = active_members_result.scalar() or 0

    check_ins_result = await db.execute(
        select(sa_func.count()).where(
            GymCheckIn.gym_id == gym_id,
            GymCheckIn.checked_in_at >= start,
        )
    )
    total_check_ins = check_ins_result.scalar() or 0

    workouts_result = await db.execute(
        select(sa_func.count()).where(
            Workout.gym_id == gym_id,
            Workout.status == WorkoutStatus.completed,
            Workout.created_at >= start,
        )
    )
    total_workouts = workouts_result.scalar() or 0

    sessions_result = await db.execute(
        select(sa_func.count()).where(
            Schedule.gym_id == gym_id,
            Schedule.status == ScheduleStatus.completed,
            Schedule.scheduled_start >= start,
        )
    )
    total_sessions = sessions_result.scalar() or 0

    return {
        "active_memberships": active_members,
        "total_check_ins": total_check_ins,
        "total_workouts": total_workouts,
        "completed_sessions": total_sessions,
        "period_days": period_days,
    }


async def get_trainer_utilization(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    start_date: datetime,
    end_date: datetime,
) -> list[dict]:
    result = await db.execute(
        select(
            Schedule.trainer_id,
            sa_func.count().label("total"),
            sa_func.count().filter(Schedule.status == ScheduleStatus.completed).label("completed"),
            sa_func.count().filter(Schedule.status == ScheduleStatus.no_show).label("no_shows"),
            sa_func.count().filter(Schedule.status == ScheduleStatus.canceled).label("canceled"),
        )
        .where(
            Schedule.gym_id == gym_id,
            Schedule.scheduled_start >= start_date,
            Schedule.scheduled_start <= end_date,
        )
        .group_by(Schedule.trainer_id)
    )
    return [
        {
            "trainer_id": str(row.trainer_id),
            "total_sessions": row.total,
            "completed": row.completed,
            "no_shows": row.no_shows,
            "canceled": row.canceled,
        }
        for row in result.all()
    ]


async def get_client_adherence(
    db: AsyncSession,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    *,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    scheduled_result = await db.execute(
        select(sa_func.count()).where(
            Schedule.gym_id == gym_id,
            Schedule.client_id == client_id,
            Schedule.scheduled_start >= start_date,
            Schedule.scheduled_start <= end_date,
        )
    )
    total_scheduled = scheduled_result.scalar() or 0

    completed_result = await db.execute(
        select(sa_func.count()).where(
            Schedule.gym_id == gym_id,
            Schedule.client_id == client_id,
            Schedule.status == ScheduleStatus.completed,
            Schedule.scheduled_start >= start_date,
            Schedule.scheduled_start <= end_date,
        )
    )
    total_completed = completed_result.scalar() or 0

    adherence_rate = (total_completed / total_scheduled * 100) if total_scheduled > 0 else 0

    return {
        "client_id": str(client_id),
        "total_scheduled": total_scheduled,
        "total_completed": total_completed,
        "adherence_rate": round(adherence_rate, 1),
    }
