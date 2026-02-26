import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.exercise import Exercise
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


async def start_workout(
    db: AsyncSession, *, workout_id: uuid.UUID, gym_id: uuid.UUID
) -> Workout | None:
    workout = await get_workout(db, gym_id, workout_id)
    if not workout:
        return None
    workout.status = WorkoutStatus.in_progress
    workout.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(workout)
    return workout


async def complete_workout(
    db: AsyncSession, *, workout_id: uuid.UUID, gym_id: uuid.UUID
) -> Workout | None:
    workout = await get_workout(db, gym_id, workout_id)
    if not workout:
        return None
    workout.status = WorkoutStatus.completed
    workout.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(workout)
    return workout


async def delete_workout_set(db: AsyncSession, *, set_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(WorkoutSet).where(WorkoutSet.set_id == set_id)
    )
    ws = result.scalar_one_or_none()
    if not ws:
        return False
    await db.delete(ws)
    await db.commit()
    return True


async def update_workout_set(
    db: AsyncSession, *, set_id: uuid.UUID, **kwargs
) -> WorkoutSet | None:
    result = await db.execute(
        select(WorkoutSet).where(WorkoutSet.set_id == set_id)
    )
    ws = result.scalar_one_or_none()
    if not ws:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(ws, key, value)
    await db.commit()
    await db.refresh(ws)
    return ws


async def detect_prs(
    db: AsyncSession,
    *,
    workout_id: uuid.UUID,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
) -> list:
    from gym_api.services.pr_service import check_and_record_prs

    exercises = await list_workout_exercises(db, workout_id)
    all_new_prs = []

    for we in exercises:
        ex_result = await db.execute(
            select(Exercise).where(Exercise.exercise_id == we.exercise_id)
        )
        exercise = ex_result.scalar_one_or_none()
        exercise_name = exercise.name if exercise else "Unknown"

        sets = await list_sets(db, we.workout_exercise_id)
        if not sets:
            continue

        best_set = None
        best_weight = 0.0
        sets_data = []
        for s in sets:
            w = float(s.weight_kg) if s.weight_kg else 0.0
            r = s.reps or 0
            sets_data.append({
                "weight_kg": w,
                "reps": r,
                "completed": s.completed if s.completed is not None else True,
            })
            if s.completed is not False and w > best_weight:
                best_weight = w
                best_set = s

        if best_set and best_weight > 0:
            new_prs = await check_and_record_prs(
                db,
                gym_id=gym_id,
                client_id=client_id,
                exercise_id=we.exercise_id,
                exercise_name=exercise_name,
                weight_kg=best_weight,
                reps=best_set.reps or 0,
                sets_data=sets_data,
            )
            all_new_prs.extend(new_prs)

    return all_new_prs
