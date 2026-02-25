import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet, WorkoutStatus
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_workout(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Workout:
    workout = Workout(gym_id=gym_id, **kwargs)
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout


async def get_workout(db: AsyncSession, gym_id: uuid.UUID, workout_id: uuid.UUID) -> Workout | None:
    result = await db.execute(
        select(Workout).where(Workout.workout_id == workout_id, Workout.gym_id == gym_id)
    )
    return result.scalar_one_or_none()


async def list_workouts(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Workout], dict]:
    query = select(Workout).where(Workout.gym_id == gym_id)
    if client_id:
        query = query.where(Workout.client_id == client_id)
    if status:
        query = query.where(Workout.status == WorkoutStatus(status))
    query = apply_cursor_pagination(
        query, order_column=Workout.created_at, cursor=cursor, limit=limit, ascending=False
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_workout(db: AsyncSession, workout: Workout, **kwargs) -> Workout:
    for key, value in kwargs.items():
        if value is not None:
            setattr(workout, key, value)
    await db.commit()
    await db.refresh(workout)
    return workout


async def add_exercise_to_workout(
    db: AsyncSession, *, workout_id: uuid.UUID, **kwargs
) -> WorkoutExercise:
    we = WorkoutExercise(workout_id=workout_id, **kwargs)
    db.add(we)
    await db.commit()
    await db.refresh(we)
    return we


async def list_workout_exercises(db: AsyncSession, workout_id: uuid.UUID) -> list[WorkoutExercise]:
    result = await db.execute(
        select(WorkoutExercise)
        .where(WorkoutExercise.workout_id == workout_id)
        .order_by(WorkoutExercise.order_index)
    )
    return list(result.scalars().all())


async def add_set(db: AsyncSession, *, workout_exercise_id: uuid.UUID, **kwargs) -> WorkoutSet:
    ws = WorkoutSet(workout_exercise_id=workout_exercise_id, **kwargs)
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return ws


async def list_sets(db: AsyncSession, workout_exercise_id: uuid.UUID) -> list[WorkoutSet]:
    result = await db.execute(
        select(WorkoutSet)
        .where(WorkoutSet.workout_exercise_id == workout_exercise_id)
        .order_by(WorkoutSet.set_index)
    )
    return list(result.scalars().all())
