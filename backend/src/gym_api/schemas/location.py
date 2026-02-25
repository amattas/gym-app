import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    name: str = Field(..., max_length=200)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    timezone: str | None = Field(None, max_length=50)
    capacity: int | None = None


class LocationUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    timezone: str | None = Field(None, max_length=50)
    capacity: int | None = None
    is_active: bool | None = None


class LocationResponse(BaseModel):
    location_id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    timezone: str | None = None
    capacity: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
