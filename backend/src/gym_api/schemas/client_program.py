import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ClientProgramCreate(BaseModel):
    program_id: uuid.UUID
    assigned_by_trainer_id: uuid.UUID | None = None


class ClientProgramResponse(BaseModel):
    client_program_id: uuid.UUID
    client_id: uuid.UUID
    program_id: uuid.UUID
    status: str
    assigned_at: datetime
    assigned_by_trainer_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class ProgramDayCreate(BaseModel):
    name: str = Field(..., max_length=200)
    order_index: int


class ProgramDayResponse(BaseModel):
    program_day_id: uuid.UUID
    program_id: uuid.UUID
    name: str
    order_index: int

    model_config = {"from_attributes": True}


class ProgramDayExerciseCreate(BaseModel):
    exercise_id: uuid.UUID
    order_index: int
    default_sets: int | None = None
    default_reps: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class ProgramDayExerciseResponse(BaseModel):
    program_day_exercise_id: uuid.UUID
    program_day_id: uuid.UUID
    exercise_id: uuid.UUID
    order_index: int
    default_sets: int | None = None
    default_reps: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}
