import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.progress_photo import ProgressPhoto
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_photo(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> ProgressPhoto:
    photo = ProgressPhoto(gym_id=gym_id, **kwargs)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def list_client_photos(
    db: AsyncSession,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[ProgressPhoto], dict]:
    query = select(ProgressPhoto).where(
        ProgressPhoto.gym_id == gym_id,
        ProgressPhoto.client_id == client_id,
    )
    query = apply_cursor_pagination(
        query, order_column=ProgressPhoto.created_at, cursor=cursor, limit=limit,
        ascending=False,
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def delete_photo(db: AsyncSession, photo: ProgressPhoto) -> None:
    await db.delete(photo)
    await db.commit()


async def get_photo(
    db: AsyncSession, gym_id: uuid.UUID, photo_id: uuid.UUID
) -> ProgressPhoto | None:
    result = await db.execute(
        select(ProgressPhoto).where(
            ProgressPhoto.photo_id == photo_id,
            ProgressPhoto.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()
