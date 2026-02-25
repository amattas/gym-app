import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.location import Location
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_location(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Location:
    location = Location(gym_id=gym_id, **kwargs)
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def get_location(
    db: AsyncSession, gym_id: uuid.UUID, location_id: uuid.UUID
) -> Location | None:
    result = await db.execute(
        select(Location).where(
            Location.location_id == location_id,
            Location.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_locations(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Location], dict]:
    query = select(Location).where(Location.gym_id == gym_id, Location.is_active.is_(True))
    query = apply_cursor_pagination(
        query, order_column=Location.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_location(db: AsyncSession, location: Location, **kwargs) -> Location:
    for key, value in kwargs.items():
        if value is not None:
            setattr(location, key, value)
    await db.commit()
    await db.refresh(location)
    return location


async def delete_location(db: AsyncSession, location: Location) -> None:
    location.is_active = False
    await db.commit()
