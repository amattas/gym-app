import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.models.user import User
from gym_api.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from gym_api.services import notification_service

router = APIRouter(tags=["notifications"])


@router.post("/v1/devices", status_code=201, response_model=dict)
async def register_device(
    body: DeviceTokenCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device = await notification_service.register_device(
        db, user_id=user.user_id, platform=body.platform, token=body.token
    )
    return {"data": DeviceTokenResponse.model_validate(device)}


@router.delete("/v1/devices/{device_token_id}", status_code=204)
async def unregister_device(
    device_token_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    device = await notification_service.get_device(db, device_token_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await notification_service.unregister_device(db, device)


@router.get("/v1/notifications/preferences", response_model=dict)
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref = await notification_service.get_preferences(db, user.user_id)
    if not pref:
        pref = await notification_service.update_preferences(db, user.user_id)
    return {"data": NotificationPreferenceResponse.model_validate(pref)}


@router.put("/v1/notifications/preferences", response_model=dict)
async def update_preferences(
    body: NotificationPreferenceUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref = await notification_service.update_preferences(
        db, user.user_id, **body.model_dump(exclude_unset=True)
    )
    return {"data": NotificationPreferenceResponse.model_validate(pref)}
