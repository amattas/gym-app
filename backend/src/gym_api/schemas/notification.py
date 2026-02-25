import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DeviceTokenCreate(BaseModel):
    platform: str = Field(..., max_length=20)
    token: str = Field(..., max_length=500)


class DeviceTokenResponse(BaseModel):
    device_token_id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    token: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationPreferenceUpdate(BaseModel):
    session_reminders: bool | None = None
    workout_updates: bool | None = None
    membership_alerts: bool | None = None
    marketing: bool | None = None


class NotificationPreferenceResponse(BaseModel):
    preference_id: uuid.UUID
    user_id: uuid.UUID
    session_reminders: bool
    workout_updates: bool
    membership_alerts: bool
    marketing: bool

    model_config = {"from_attributes": True}
