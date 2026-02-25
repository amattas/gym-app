import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.account import Account
from gym_api.models.client import Client


async def create_account(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Account:
    account = Account(gym_id=gym_id, **kwargs)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_account(
    db: AsyncSession, gym_id: uuid.UUID, account_id: uuid.UUID
) -> Account | None:
    result = await db.execute(
        select(Account).where(
            Account.account_id == account_id,
            Account.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_account_members(
    db: AsyncSession, gym_id: uuid.UUID, account_id: uuid.UUID
) -> list[Client]:
    result = await db.execute(
        select(Client).where(
            Client.gym_id == gym_id,
            Client.deleted_at.is_(None),
        )
    )
    return list(result.scalars().all())
