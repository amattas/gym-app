import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MembershipCreate(BaseModel):
    plan_template_id: uuid.UUID
    started_at: datetime | None = None
    base_membership_id: uuid.UUID | None = None


class MembershipUpdate(BaseModel):
    status: str | None = None


class MembershipPause(BaseModel):
    reason: str | None = Field(None, max_length=500)


class MembershipCancel(BaseModel):
    reason: str | None = Field(None, max_length=500)
    cancel_immediately: bool = False


class MembershipResponse(BaseModel):
    client_membership_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    plan_template_id: uuid.UUID
    plan_type: str
    status: str
    started_at: datetime
    expires_at: datetime | None = None
    visit_entitlement: dict | None = None
    visits_used_this_period: int
    total_visits_remaining: int | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    pause_info: dict | None = None
    cancellation_info: dict | None = None
    base_membership_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntitlementResponse(BaseModel):
    client_membership_id: uuid.UUID
    plan_type: str
    status: str
    visit_entitlement: dict | None = None
    visits_used_this_period: int
    total_visits_remaining: int | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None

    model_config = {"from_attributes": True}


class RecordVisitRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)
