import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client import Client, ClientStatus
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_client(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Client:
    client = Client(gym_id=gym_id, **kwargs)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def get_client(db: AsyncSession, gym_id: uuid.UUID, client_id: uuid.UUID) -> Client | None:
    result = await db.execute(
        select(Client).where(
            Client.client_id == client_id,
            Client.gym_id == gym_id,
            Client.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def list_clients(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    search: str | None = None,
    status: str | None = None,
    trainer_id: uuid.UUID | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Client], dict]:
    query = select(Client).where(Client.gym_id == gym_id, Client.deleted_at.is_(None))
    if search:
        pattern = f"%{search}%"
        from sqlalchemy import or_

        query = query.where(
            or_(
                Client.first_name.ilike(pattern),
                Client.last_name.ilike(pattern),
                Client.email.ilike(pattern),
                Client.phone.ilike(pattern),
            )
        )
    if status:
        query = query.where(Client.status == status)
    if trainer_id:
        from gym_api.models.trainer_client import TrainerClientAssignment

        subq = (
            select(TrainerClientAssignment.client_id)
            .where(TrainerClientAssignment.trainer_id == trainer_id)
            .scalar_subquery()
        )
        query = query.where(Client.client_id.in_(subq))
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
    client.deleted_at = datetime.now(timezone.utc)
    client.status = ClientStatus.inactive
    await db.commit()
