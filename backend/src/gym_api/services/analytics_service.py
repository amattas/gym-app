import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.check_in import GymCheckIn
from gym_api.models.client import Client
from gym_api.models.client_membership import ClientMembership
from gym_api.models.measurement import Measurement, MeasurementType
from gym_api.models.schedule import Schedule, ScheduleStatus
from gym_api.models.trainer import Trainer
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet, WorkoutStatus


def compute_workout_analytics(
    exercises: list[dict],
    sets_by_exercise: dict[str, list[dict]],
) -> dict:
    total_volume = 0.0
    total_sets = 0
    total_reps = 0
    exercise_summaries = []

    for ex in exercises:
        ex_id = str(ex["workout_exercise_id"])
        ex_sets = sets_by_exercise.get(ex_id, [])
        ex_volume = 0.0
        ex_reps = 0
        completed_sets = 0

        for s in ex_sets:
            w = s.get("weight_kg") or 0
            r = s.get("reps") or 0
            if s.get("completed", True):
                ex_volume += w * r
                ex_reps += r
                completed_sets += 1

        total_volume += ex_volume
        total_sets += completed_sets
        total_reps += ex_reps

        exercise_summaries.append(
            {
                "exercise_id": str(ex.get("exercise_id", "")),
                "order_index": ex.get("order_index", 0),
                "completed_sets": completed_sets,
                "total_reps": ex_reps,
                "volume_kg": round(ex_volume, 2),
            }
        )

    return {
        "total_volume_kg": round(total_volume, 2),
        "total_sets": total_sets,
        "total_reps": total_reps,
        "exercises": exercise_summaries,
    }


async def get_client_workout_stats(
    db: AsyncSession,
    *,
    client_id: uuid.UUID,
    gym_id: uuid.UUID,
    days: int = 30,
) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total_result = await db.execute(
        select(sa_func.count()).where(
            Workout.client_id == client_id,
            Workout.gym_id == gym_id,
            Workout.created_at >= since,
        )
    )
    total_workouts = total_result.scalar() or 0

    completed_result = await db.execute(
        select(sa_func.count()).where(
            Workout.client_id == client_id,
            Workout.gym_id == gym_id,
            Workout.created_at >= since,
            Workout.status == WorkoutStatus.completed,
        )
    )
    completed_workouts = completed_result.scalar() or 0

    avg_result = await db.execute(
        select(
            sa_func.avg(
                sa_func.extract("epoch", Workout.ended_at)
                - sa_func.extract("epoch", Workout.started_at)
            )
        ).where(
            Workout.client_id == client_id,
            Workout.gym_id == gym_id,
            Workout.created_at >= since,
            Workout.status == WorkoutStatus.completed,
            Workout.started_at.isnot(None),
            Workout.ended_at.isnot(None),
        )
    )
    avg_seconds = avg_result.scalar()
    avg_duration = round(avg_seconds / 60, 1) if avg_seconds else None

    completion_rate = (
        round(completed_workouts / total_workouts, 2)
        if total_workouts > 0
        else 0.0
    )

    return {
        "total_workouts": total_workouts,
        "completed_workouts": completed_workouts,
        "avg_duration_minutes": avg_duration,
        "completion_rate": completion_rate,
    }


async def get_client_volume_trend(
    db: AsyncSession,
    *,
    client_id: uuid.UUID,
    gym_id: uuid.UUID,
    days: int = 30,
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Workout).where(
            Workout.client_id == client_id,
            Workout.gym_id == gym_id,
            Workout.created_at >= since,
            Workout.status == WorkoutStatus.completed,
        ).order_by(Workout.created_at)
    )
    workouts = result.scalars().all()

    daily_volumes: dict[str, float] = {}
    for w in workouts:
        day_key = w.created_at.date().isoformat()
        ex_result = await db.execute(
            select(WorkoutExercise).where(
                WorkoutExercise.workout_id == w.workout_id
            )
        )
        exercises = ex_result.scalars().all()
        volume = 0.0
        for ex in exercises:
            sets_result = await db.execute(
                select(WorkoutSet).where(
                    WorkoutSet.workout_exercise_id
                    == ex.workout_exercise_id
                )
            )
            for s in sets_result.scalars().all():
                wt = float(s.weight_kg) if s.weight_kg else 0.0
                r = s.reps or 0
                if s.completed is not False:
                    volume += wt * r
        daily_volumes[day_key] = (
            daily_volumes.get(day_key, 0.0) + volume
        )

    return [
        {"date": d, "total_volume_kg": round(v, 2)}
        for d, v in sorted(daily_volumes.items())
    ]


async def get_client_measurement_trend(
    db: AsyncSession,
    *,
    client_id: uuid.UUID,
    measurement_type: str,
    days: int = 90,
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Measurement).where(
            Measurement.client_id == client_id,
            Measurement.type == MeasurementType(measurement_type),
            Measurement.measured_at >= since,
        ).order_by(Measurement.measured_at)
    )
    measurements = result.scalars().all()

    return [
        {
            "date": m.measured_at,
            "value": float(m.value),
            "unit": m.unit,
        }
        for m in measurements
    ]


async def get_gym_dashboard(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    days: int = 30,
) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    active_result = await db.execute(
        select(sa_func.count(Client.client_id.distinct())).where(
            Client.gym_id == gym_id,
            Client.status == "active",
            Client.deleted_at.is_(None),
        )
    )
    active_clients = active_result.scalar() or 0

    workout_result = await db.execute(
        select(sa_func.count()).where(
            Workout.gym_id == gym_id,
            Workout.created_at >= since,
        )
    )
    total_workouts = workout_result.scalar() or 0

    checkin_result = await db.execute(
        select(sa_func.count()).where(
            GymCheckIn.gym_id == gym_id,
            GymCheckIn.checked_in_at >= since,
        )
    )
    total_check_ins = checkin_result.scalar() or 0

    membership_result = await db.execute(
        select(sa_func.count()).where(
            ClientMembership.gym_id == gym_id,
            ClientMembership.created_at >= since,
        )
    )
    new_memberships = membership_result.scalar() or 0

    return {
        "active_clients": active_clients,
        "total_workouts": total_workouts,
        "total_check_ins": total_check_ins,
        "new_memberships": new_memberships,
    }


async def get_trainer_utilization(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    days: int = 30,
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    trainer_result = await db.execute(
        select(Trainer).where(
            Trainer.gym_id == gym_id,
            Trainer.is_active.is_(True),
        )
    )
    trainers = trainer_result.scalars().all()

    results = []
    for t in trainers:
        scheduled_result = await db.execute(
            select(sa_func.count()).where(
                Schedule.trainer_id == t.trainer_id,
                Schedule.gym_id == gym_id,
                Schedule.scheduled_start >= since,
            )
        )
        scheduled = scheduled_result.scalar() or 0

        completed_result = await db.execute(
            select(sa_func.count()).where(
                Schedule.trainer_id == t.trainer_id,
                Schedule.gym_id == gym_id,
                Schedule.scheduled_start >= since,
                Schedule.status == ScheduleStatus.completed,
            )
        )
        completed = completed_result.scalar() or 0

        no_show_result = await db.execute(
            select(sa_func.count()).where(
                Schedule.trainer_id == t.trainer_id,
                Schedule.gym_id == gym_id,
                Schedule.scheduled_start >= since,
                Schedule.status == ScheduleStatus.no_show,
            )
        )
        no_shows = no_show_result.scalar() or 0

        results.append({
            "trainer_id": t.trainer_id,
            "trainer_name": f"{t.first_name} {t.last_name}",
            "sessions_scheduled": scheduled,
            "sessions_completed": completed,
            "no_shows": no_shows,
        })

    return results
