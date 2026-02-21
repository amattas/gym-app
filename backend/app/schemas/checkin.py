"""Pydantic schemas for check-in request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CheckInCreate(BaseModel):
    """Schema for creating a new check-in record."""

    client_id: uuid.UUID
    gym_id: uuid.UUID
    location_id: uuid.UUID | None = None
    training_session_id: uuid.UUID | None = None
    check_in_time: datetime | None = None
    is_walk_in: bool = True
    notes: str | None = None


class CheckOutUpdate(BaseModel):
    """Schema for updating a check-in with check-out information."""

    check_out_time: datetime | None = None
    notes: str | None = None


class CheckInListFilters(BaseModel):
    """Filters for listing check-in records."""

    gym_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    checked_in_by: uuid.UUID | None = None
    is_walk_in: bool | None = None
    is_active: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class TrainingSessionSummary(BaseModel):
    """Minimal training session info for embedding in responses."""

    id: uuid.UUID
    scheduled_start: datetime
    scheduled_end: datetime
    status: str

    model_config = {"from_attributes": True}


class ClientSearchResult(BaseModel):
    """Client search result with current check-in and session status."""

    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    status: str
    has_active_checkin: bool = False
    scheduled_session: TrainingSessionSummary | None = None

    model_config = {"from_attributes": True}


class CheckInResponse(BaseModel):
    """Full check-in record response schema."""

    id: uuid.UUID
    gym_id: uuid.UUID
    location_id: uuid.UUID | None = None
    client_id: uuid.UUID
    checked_in_by: uuid.UUID
    check_in_time: datetime
    check_out_time: datetime | None = None
    training_session_id: uuid.UUID | None = None
    is_walk_in: bool
    notes: str | None = None
    duration_minutes: int | None = None

    model_config = {"from_attributes": True}
