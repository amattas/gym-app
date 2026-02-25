import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.cache.cache_service import cache_delete
from gym_api.models.exercise import Exercise
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


def _cache_key(exercise_id: uuid.UUID) -> str:
    return f"exercise:{exercise_id}"


async def create_exercise(
    db: AsyncSession, *, gym_id: uuid.UUID | None = None, **kwargs
) -> Exercise:
    exercise = Exercise(gym_id=gym_id, **kwargs)
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def get_exercise(db: AsyncSession, exercise_id: uuid.UUID) -> Exercise | None:
    result = await db.execute(select(Exercise).where(Exercise.exercise_id == exercise_id))
    return result.scalar_one_or_none()


async def list_exercises(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Exercise], dict]:
    # Show global exercises (gym_id=None) plus gym-specific ones
    query = select(Exercise).where(or_(Exercise.gym_id == gym_id, Exercise.gym_id.is_(None)))
    query = apply_cursor_pagination(
        query, order_column=Exercise.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_exercise(db: AsyncSession, exercise: Exercise, **kwargs) -> Exercise:
    for key, value in kwargs.items():
        if value is not None:
            setattr(exercise, key, value)
    await db.commit()
    await db.refresh(exercise)
    await cache_delete(_cache_key(exercise.exercise_id))
    return exercise


async def delete_exercise(db: AsyncSession, exercise: Exercise) -> None:
    exercise_id = exercise.exercise_id
    await db.delete(exercise)
    await db.commit()
    await cache_delete(_cache_key(exercise_id))
