import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.plan_template import PlanTemplate
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_plan_template(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> PlanTemplate:
    template = PlanTemplate(gym_id=gym_id, **kwargs)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_plan_template(
    db: AsyncSession, gym_id: uuid.UUID, plan_template_id: uuid.UUID
) -> PlanTemplate | None:
    result = await db.execute(
        select(PlanTemplate).where(
            PlanTemplate.plan_template_id == plan_template_id,
            PlanTemplate.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_plan_templates(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    status: str | None = None,
    plan_type: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[PlanTemplate], dict]:
    query = select(PlanTemplate).where(PlanTemplate.gym_id == gym_id)
    if status:
        query = query.where(PlanTemplate.status == status)
    if plan_type:
        query = query.where(PlanTemplate.plan_type == plan_type)
    query = apply_cursor_pagination(
        query, order_column=PlanTemplate.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_plan_template(
    db: AsyncSession, template: PlanTemplate, **kwargs
) -> PlanTemplate:
    for key, value in kwargs.items():
        if value is not None:
            setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_plan_template(db: AsyncSession, template: PlanTemplate) -> None:
    await db.delete(template)
    await db.commit()
