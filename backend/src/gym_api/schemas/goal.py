import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    goal_type: str = Field(..., max_length=100)
    target_value: float | None = None
    current_value: float | None = None
    target_date: date | None = None
    notes: str | None = None
    created_by_trainer_id: uuid.UUID | None = None


class GoalUpdate(BaseModel):
    goal_type: str | None = Field(None, max_length=100)
    target_value: float | None = None
    current_value: float | None = None
    target_date: date | None = None
    status: str | None = None
    notes: str | None = None


class GoalResponse(BaseModel):
    goal_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    goal_type: str
    target_value: float | None = None
    current_value: float | None = None
    target_date: date | None = None
    status: str
    notes: str | None = None
    created_by_trainer_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
