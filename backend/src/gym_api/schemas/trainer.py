import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TrainerCreate(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255)
    specializations: str | None = Field(None, max_length=500)


class TrainerUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    specializations: str | None = Field(None, max_length=500)


class TrainerResponse(BaseModel):
    trainer_id: uuid.UUID
    gym_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    specializations: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
