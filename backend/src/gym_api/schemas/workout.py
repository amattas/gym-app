import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    client_id: uuid.UUID
    trainer_id: uuid.UUID | None = None
    program_id: uuid.UUID | None = None
    notes: str | None = Field(None, max_length=1000)


class WorkoutUpdate(BaseModel):
    status: str | None = None
    notes: str | None = Field(None, max_length=1000)
    started_at: datetime | None = None
    ended_at: datetime | None = None


class WorkoutExerciseCreate(BaseModel):
    exercise_id: uuid.UUID
    order_index: int
    target_sets: int | None = None
    target_reps: int | None = None


class WorkoutSetCreate(BaseModel):
    set_index: int
    weight_kg: float | None = None
    reps: int | None = None
    duration_seconds: int | None = None
    completed: bool = True


class WorkoutSetResponse(BaseModel):
    set_id: uuid.UUID
    workout_exercise_id: uuid.UUID
    set_index: int
    weight_kg: float | None = None
    reps: int | None = None
    duration_seconds: int | None = None
    completed: bool | None = None

    model_config = {"from_attributes": True}


class WorkoutExerciseResponse(BaseModel):
    workout_exercise_id: uuid.UUID
    workout_id: uuid.UUID
    exercise_id: uuid.UUID
    order_index: int
    target_sets: int | None = None
    target_reps: int | None = None

    model_config = {"from_attributes": True}


class WorkoutResponse(BaseModel):
    workout_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    trainer_id: uuid.UUID | None = None
    program_id: uuid.UUID | None = None
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
