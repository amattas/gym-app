import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    muscle_groups: list[str] | None = None
    equipment: str | None = Field(None, max_length=200)


class ExerciseUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    muscle_groups: list[str] | None = None
    equipment: str | None = Field(None, max_length=200)


class ExerciseResponse(BaseModel):
    exercise_id: uuid.UUID
    gym_id: uuid.UUID | None = None
    name: str
    description: str | None = None
    muscle_groups: list[str] | None = None
    equipment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
