import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.notification import DeviceToken, NotificationPreference


async def register_device(
    db: AsyncSession, *, user_id: uuid.UUID, platform: str, token: str
) -> DeviceToken:
    device = DeviceToken(user_id=user_id, platform=platform, token=token)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


async def unregister_device(db: AsyncSession, device: DeviceToken) -> None:
    await db.delete(device)
    await db.commit()


async def get_device(db: AsyncSession, device_token_id: uuid.UUID) -> DeviceToken | None:
    result = await db.execute(
        select(DeviceToken).where(DeviceToken.device_token_id == device_token_id)
    )
    return result.scalar_one_or_none()


async def get_preferences(
    db: AsyncSession, user_id: uuid.UUID
) -> NotificationPreference | None:
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_preferences(
    db: AsyncSession, user_id: uuid.UUID, **kwargs
) -> NotificationPreference:
    pref = await get_preferences(db, user_id)
    if not pref:
        pref = NotificationPreference(user_id=user_id, **kwargs)
        db.add(pref)
    else:
        for key, value in kwargs.items():
            if value is not None:
                setattr(pref, key, value)
    await db.commit()
    await db.refresh(pref)
    return pref
