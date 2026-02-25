import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client import Client
from gym_api.models.trainer_client import TrainerClientAssignment
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def assign_trainer_to_client(
    db: AsyncSession,
    *,
    trainer_id: uuid.UUID,
    client_id: uuid.UUID,
    assigned_by: uuid.UUID | None = None,
    is_primary: bool = False,
) -> TrainerClientAssignment:
    existing = await db.execute(
        select(TrainerClientAssignment).where(
            TrainerClientAssignment.trainer_id == trainer_id,
            TrainerClientAssignment.client_id == client_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Trainer is already assigned to this client")

    assignment = TrainerClientAssignment(
        trainer_id=trainer_id,
        client_id=client_id,
        assigned_by=assigned_by,
        is_primary=is_primary,
        assigned_at=datetime.now(timezone.utc),
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def unassign_trainer_from_client(
    db: AsyncSession, *, trainer_id: uuid.UUID, client_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(TrainerClientAssignment).where(
            TrainerClientAssignment.trainer_id == trainer_id,
            TrainerClientAssignment.client_id == client_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise ValueError("Assignment not found")
    await db.delete(assignment)
    await db.commit()


async def list_trainer_clients(
    db: AsyncSession,
    gym_id: uuid.UUID,
    trainer_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Client], dict]:
    subq = (
        select(TrainerClientAssignment.client_id)
        .where(TrainerClientAssignment.trainer_id == trainer_id)
        .scalar_subquery()
    )
    query = select(Client).where(
        Client.gym_id == gym_id,
        Client.client_id.in_(subq),
        Client.deleted_at.is_(None),
    )
    query = apply_cursor_pagination(
        query, order_column=Client.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination
