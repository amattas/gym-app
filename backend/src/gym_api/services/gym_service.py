import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.gym import Gym
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_gym(db: AsyncSession, *, name: str, slug: str, **kwargs) -> Gym:
    existing = await db.execute(select(Gym).where(Gym.slug == slug))
    if existing.scalar_one_or_none():
        raise ValueError("Gym slug already exists")
    gym = Gym(name=name, slug=slug, **kwargs)
    db.add(gym)
    await db.commit()
    await db.refresh(gym)
    return gym


async def get_gym(db: AsyncSession, gym_id: uuid.UUID) -> Gym | None:
    result = await db.execute(select(Gym).where(Gym.gym_id == gym_id))
    return result.scalar_one_or_none()


async def list_gyms(
    db: AsyncSession, *, cursor: str | None = None, limit: int = 20
) -> tuple[list[Gym], dict]:
    query = select(Gym).where(Gym.is_active.is_(True))
    query = apply_cursor_pagination(query, order_column=Gym.created_at, cursor=cursor, limit=limit)
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_gym(db: AsyncSession, gym: Gym, **kwargs) -> Gym:
    for key, value in kwargs.items():
        if value is not None:
            setattr(gym, key, value)
    await db.commit()
    await db.refresh(gym)
    return gym
