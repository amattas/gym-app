import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.goal import ClientGoal
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_goal(
    db: AsyncSession, *, gym_id: uuid.UUID, client_id: uuid.UUID, **kwargs
) -> ClientGoal:
    goal = ClientGoal(gym_id=gym_id, client_id=client_id, **kwargs)
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_goal(db: AsyncSession, gym_id: uuid.UUID, goal_id: uuid.UUID) -> ClientGoal | None:
    result = await db.execute(
        select(ClientGoal).where(
            ClientGoal.goal_id == goal_id,
            ClientGoal.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_client_goals(
    db: AsyncSession,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[ClientGoal], dict]:
    query = select(ClientGoal).where(
        ClientGoal.gym_id == gym_id,
        ClientGoal.client_id == client_id,
    )
    query = apply_cursor_pagination(
        query, order_column=ClientGoal.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_goal(db: AsyncSession, goal: ClientGoal, **kwargs) -> ClientGoal:
    for key, value in kwargs.items():
        if value is not None:
            setattr(goal, key, value)
    await db.commit()
    await db.refresh(goal)
    return goal


async def delete_goal(db: AsyncSession, goal: ClientGoal) -> None:
    await db.delete(goal)
    await db.commit()
