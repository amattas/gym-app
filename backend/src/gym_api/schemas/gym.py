import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GymCreate(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=100)
    unit_system: str = Field("imperial", pattern="^(metric|imperial)$")
    timezone: str = Field("America/New_York", max_length=50)
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None


class GymUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    unit_system: str | None = Field(None, pattern="^(metric|imperial)$")
    timezone: str | None = Field(None, max_length=50)
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    settings: dict | None = None


class GymResponse(BaseModel):
    gym_id: uuid.UUID
    name: str
    slug: str
    unit_system: str
    timezone: str
    is_active: bool
    settings: dict | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
