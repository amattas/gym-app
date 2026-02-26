import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.ai_summary import WorkoutSummary
from gym_api.models.exercise import Exercise
from gym_api.models.personal_record import PersonalRecord
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet, WorkoutStatus


async def get_client_summary(
    db: AsyncSession, gym_id: uuid.UUID, client_id: uuid.UUID
) -> WorkoutSummary | None:
    result = await db.execute(
        select(WorkoutSummary)
        .where(
            WorkoutSummary.gym_id == gym_id,
            WorkoutSummary.client_id == client_id,
            WorkoutSummary.is_stale.is_(False),
        )
        .order_by(WorkoutSummary.generated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_summary(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    content: str,
    model_used: str | None = None,
) -> WorkoutSummary:
    existing = await db.execute(
        select(WorkoutSummary).where(
            WorkoutSummary.gym_id == gym_id,
            WorkoutSummary.client_id == client_id,
            WorkoutSummary.is_stale.is_(False),
        )
    )
    for old in existing.scalars().all():
        old.is_stale = True

    summary = WorkoutSummary(
        gym_id=gym_id,
        client_id=client_id,
        content=content,
        model_used=model_used,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary


async def update_summary(
    db: AsyncSession, summary: WorkoutSummary, *, content: str
) -> WorkoutSummary:
    summary.content = content
    await db.commit()
    await db.refresh(summary)
    return summary


async def get_summary_by_id(
    db: AsyncSession, summary_id: uuid.UUID
) -> WorkoutSummary | None:
    result = await db.execute(
        select(WorkoutSummary).where(WorkoutSummary.summary_id == summary_id)
    )
    return result.scalar_one_or_none()


async def generate_client_summary(
    db: AsyncSession, gym_id: uuid.UUID, client_id: uuid.UUID, *, days: int = 30
) -> WorkoutSummary:
    content = await _build_summary_text(db, client_id, days=days)
    return await create_summary(
        db, gym_id=gym_id, client_id=client_id,
        content=content, model_used="data-driven-v1",
    )


async def _build_summary_text(
    db: AsyncSession, client_id: uuid.UUID, *, days: int = 30
) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Workout).where(
            Workout.client_id == client_id,
            Workout.status == WorkoutStatus.completed,
            Workout.started_at >= cutoff,
        ).order_by(Workout.started_at.desc())
    )
    workouts = result.scalars().all()

    if not workouts:
        return f"No completed workouts in the last {days} days."

    total_workouts = len(workouts)
    total_sets = 0
    total_volume_kg = 0.0
    exercise_counts: dict[uuid.UUID, int] = {}

    for w in workouts:
        ex_result = await db.execute(
            select(WorkoutExercise).where(
                WorkoutExercise.workout_id == w.workout_id
            )
        )
        exercises = ex_result.scalars().all()
        for ex in exercises:
            exercise_counts[ex.exercise_id] = (
                exercise_counts.get(ex.exercise_id, 0) + 1
            )
            set_result = await db.execute(
                select(WorkoutSet).where(
                    WorkoutSet.workout_exercise_id == ex.workout_exercise_id,
                    WorkoutSet.completed.is_(True),
                )
            )
            sets = set_result.scalars().all()
            total_sets += len(sets)
            for s in sets:
                if s.weight_kg and s.reps:
                    total_volume_kg += float(s.weight_kg) * s.reps

    top_exercise_ids = sorted(
        exercise_counts, key=exercise_counts.get, reverse=True
    )[:5]
    exercise_names = {}
    if top_exercise_ids:
        name_result = await db.execute(
            select(Exercise.exercise_id, Exercise.name).where(
                Exercise.exercise_id.in_(top_exercise_ids)
            )
        )
        exercise_names = dict(name_result.all())

    pr_result = await db.execute(
        select(func.count()).select_from(PersonalRecord).where(
            PersonalRecord.client_id == client_id,
            PersonalRecord.achieved_at >= cutoff,
        )
    )
    pr_count = pr_result.scalar() or 0

    first_date = workouts[-1].started_at
    last_date = workouts[0].started_at
    date_range = (last_date - first_date).days + 1 if first_date and last_date else days
    freq = total_workouts / max(date_range / 7, 1)

    lines = [f"Workout Summary ({days}-day period)"]
    lines.append(f"Total workouts: {total_workouts} ({freq:.1f}/week)")
    lines.append(f"Total sets completed: {total_sets}")
    if total_volume_kg > 0:
        lines.append(f"Total volume: {total_volume_kg:,.0f} kg")
    if pr_count:
        lines.append(f"Personal records set: {pr_count}")

    if top_exercise_ids:
        lines.append("Most trained exercises:")
        for eid in top_exercise_ids:
            name = exercise_names.get(eid, str(eid)[:8])
            lines.append(f"  - {name} ({exercise_counts[eid]} sessions)")

    return "\n".join(lines)
