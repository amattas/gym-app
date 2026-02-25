import uuid
from datetime import datetime, time

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    client_id: uuid.UUID
    trainer_id: uuid.UUID
    location_id: uuid.UUID | None = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: str | None = None
    notes: str | None = None


class ScheduleUpdate(BaseModel):
    location_id: uuid.UUID | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    notes: str | None = None


class ScheduleResponse(BaseModel):
    schedule_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    trainer_id: uuid.UUID
    location_id: uuid.UUID | None = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    notes: str | None = None
    created_by_user_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrainerAvailabilityEntry(BaseModel):
    day_of_week: int
    location_id: uuid.UUID | None = None
    start_time: time
    end_time: time


class TrainerAvailabilityResponse(BaseModel):
    trainer_id: uuid.UUID
    day_of_week: int
    location_id: uuid.UUID | None = None
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class TrainerExceptionCreate(BaseModel):
    exception_date: datetime
    exception_type: str
    reason: str | None = Field(None, max_length=500)


class TrainerExceptionResponse(BaseModel):
    trainer_exception_id: uuid.UUID
    trainer_id: uuid.UUID
    exception_date: datetime
    exception_type: str
    reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
