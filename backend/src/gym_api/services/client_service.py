import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client import Client
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_client(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Client:
    client = Client(gym_id=gym_id, **kwargs)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def get_client(db: AsyncSession, gym_id: uuid.UUID, client_id: uuid.UUID) -> Client | None:
    result = await db.execute(
        select(Client).where(Client.client_id == client_id, Client.gym_id == gym_id)
    )
    return result.scalar_one_or_none()


async def list_clients(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Client], dict]:
    query = select(Client).where(Client.gym_id == gym_id)
    query = apply_cursor_pagination(
        query, order_column=Client.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_client(db: AsyncSession, client: Client, **kwargs) -> Client:
    for key, value in kwargs.items():
        if value is not None:
            setattr(client, key, value)
    await db.commit()
    await db.refresh(client)
    return client


async def delete_client(db: AsyncSession, client: Client) -> None:
    await db.delete(client)
    await db.commit()
