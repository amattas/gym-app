import uuid
from datetime import datetime

from pydantic import BaseModel


class CheckInCreate(BaseModel):
    client_id: uuid.UUID
    location_id: uuid.UUID | None = None
    schedule_id: uuid.UUID | None = None
    check_in_method: str | None = None


class CheckInResponse(BaseModel):
    check_in_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    location_id: uuid.UUID | None = None
    schedule_id: uuid.UUID | None = None
    check_in_method: str
    checked_in_by_user_id: uuid.UUID | None = None
    checked_in_at: datetime
    checked_out_at: datetime | None = None

    model_config = {"from_attributes": True}


class OccupancyResponse(BaseModel):
    location_id: uuid.UUID
    active_count: int
