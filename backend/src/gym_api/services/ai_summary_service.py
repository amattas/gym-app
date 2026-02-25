import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.ai_summary import WorkoutSummary


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
