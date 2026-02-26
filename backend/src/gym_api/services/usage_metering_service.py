import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.usage_metric import UsageMetricRollup


async def record_metric(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    metric_name: str,
    period_start: datetime,
    period_end: datetime,
    value: int = 1,
    limit_value: int | None = None,
) -> UsageMetricRollup:
    result = await db.execute(
        select(UsageMetricRollup).where(
            UsageMetricRollup.gym_id == gym_id,
            UsageMetricRollup.metric_name == metric_name,
            UsageMetricRollup.period_start == period_start,
            UsageMetricRollup.period_end == period_end,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.value += value
        if limit_value is not None:
            existing.limit_value = limit_value
        await db.commit()
        await db.refresh(existing)
        return existing

    rollup = UsageMetricRollup(
        gym_id=gym_id,
        metric_name=metric_name,
        period_start=period_start,
        period_end=period_end,
        value=value,
        limit_value=limit_value,
    )
    db.add(rollup)
    await db.commit()
    await db.refresh(rollup)
    return rollup


async def get_usage_summary(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> list[UsageMetricRollup]:
    query = select(UsageMetricRollup).where(UsageMetricRollup.gym_id == gym_id)
    if period_start:
        query = query.where(UsageMetricRollup.period_start >= period_start)
    if period_end:
        query = query.where(UsageMetricRollup.period_end <= period_end)
    query = query.order_by(
        UsageMetricRollup.metric_name, UsageMetricRollup.period_start
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_current_period_usage(
    db: AsyncSession, gym_id: uuid.UUID, *, metric_name: str
) -> UsageMetricRollup | None:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UsageMetricRollup).where(
            UsageMetricRollup.gym_id == gym_id,
            UsageMetricRollup.metric_name == metric_name,
            UsageMetricRollup.period_start <= now,
            UsageMetricRollup.period_end > now,
        )
    )
    return result.scalar_one_or_none()


async def check_limit(
    db: AsyncSession, gym_id: uuid.UUID, *, metric_name: str
) -> dict:
    usage = await get_current_period_usage(db, gym_id, metric_name=metric_name)
    if not usage:
        return {"within_limit": True, "current": 0, "limit": None}
    if usage.limit_value is None:
        return {"within_limit": True, "current": usage.value, "limit": None}
    return {
        "within_limit": usage.value < usage.limit_value,
        "current": usage.value,
        "limit": usage.limit_value,
    }


async def get_metric_totals(
    db: AsyncSession, gym_id: uuid.UUID
) -> list[dict]:
    result = await db.execute(
        select(
            UsageMetricRollup.metric_name,
            func.sum(UsageMetricRollup.value).label("total"),
            func.max(UsageMetricRollup.limit_value).label("limit_value"),
        )
        .where(UsageMetricRollup.gym_id == gym_id)
        .group_by(UsageMetricRollup.metric_name)
    )
    return [
        {"metric_name": row.metric_name, "total": row.total, "limit": row.limit_value}
        for row in result.all()
    ]
