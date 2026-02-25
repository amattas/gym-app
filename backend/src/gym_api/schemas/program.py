import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProgramCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    template_scope: str = "personal"
    num_days: int = Field(1, ge=1)
    periodization_config: dict | None = None


class ProgramUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    template_scope: str | None = None
    num_days: int | None = Field(None, ge=1)
    periodization_config: dict | None = None


class ProgramResponse(BaseModel):
    program_id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    description: str | None = None
    created_by_trainer_id: uuid.UUID | None = None
    template_scope: str
    num_days: int
    periodization_config: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
