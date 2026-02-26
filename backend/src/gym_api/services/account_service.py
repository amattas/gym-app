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
            Client.account_id == account_id,
            Client.deleted_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def add_member(
    db: AsyncSession, *, account_id: uuid.UUID, client_id: uuid.UUID
) -> Client | None:
    result = await db.execute(
        select(Client).where(Client.client_id == client_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        return None
    client.account_id = account_id
    await db.commit()
    await db.refresh(client)
    return client


async def remove_member(
    db: AsyncSession, *, account_id: uuid.UUID, client_id: uuid.UUID
) -> Client | None:
    result = await db.execute(
        select(Client).where(
            Client.client_id == client_id,
            Client.account_id == account_id,
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        return None
    client.account_id = None
    await db.commit()
    await db.refresh(client)
    return client


async def update_account(
    db: AsyncSession,
    *,
    account_id: uuid.UUID,
    gym_id: uuid.UUID,
    **kwargs,
) -> Account | None:
    result = await db.execute(
        select(Account).where(
            Account.account_id == account_id,
            Account.gym_id == gym_id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(account, key, value)
    await db.commit()
    await db.refresh(account)
    return account
