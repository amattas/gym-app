import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.trainer import Trainer
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_trainer(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Trainer:
    trainer = Trainer(gym_id=gym_id, **kwargs)
    db.add(trainer)
    await db.commit()
    await db.refresh(trainer)
    return trainer


async def get_trainer(db: AsyncSession, gym_id: uuid.UUID, trainer_id: uuid.UUID) -> Trainer | None:
    result = await db.execute(
        select(Trainer).where(Trainer.trainer_id == trainer_id, Trainer.gym_id == gym_id)
    )
    return result.scalar_one_or_none()


async def list_trainers(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Trainer], dict]:
    query = select(Trainer).where(Trainer.gym_id == gym_id, Trainer.is_active.is_(True))
    query = apply_cursor_pagination(
        query, order_column=Trainer.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_trainer(db: AsyncSession, trainer: Trainer, **kwargs) -> Trainer:
    for key, value in kwargs.items():
        if value is not None:
            setattr(trainer, key, value)
    await db.commit()
    await db.refresh(trainer)
    return trainer
