import uuid
from datetime import date, datetime

from pydantic import BaseModel


class WorkoutStats(BaseModel):
    total_workouts: int
    completed_workouts: int
    avg_duration_minutes: float | None = None
    completion_rate: float

    model_config = {"from_attributes": True}


class VolumeTrendPoint(BaseModel):
    date: date
    total_volume_kg: float

    model_config = {"from_attributes": True}


class MeasurementTrendPoint(BaseModel):
    date: datetime
    value: float
    unit: str

    model_config = {"from_attributes": True}


class GymDashboard(BaseModel):
    active_clients: int
    total_workouts: int
    total_check_ins: int
    new_memberships: int

    model_config = {"from_attributes": True}


class TrainerUtilization(BaseModel):
    trainer_id: uuid.UUID
    trainer_name: str
    sessions_scheduled: int
    sessions_completed: int
    no_shows: int

    model_config = {"from_attributes": True}


class OccupancyHistoryPoint(BaseModel):
    hour: int
    count: int

    model_config = {"from_attributes": True}


class BusynessSlot(BaseModel):
    time_slot: str
    check_ins: int
    scheduled: int
    total: int

    model_config = {"from_attributes": True}


class LatestMeasurement(BaseModel):
    measurement_id: uuid.UUID
    type: str
    value: float
    unit: str
    bmi: float | None = None
    measured_at: datetime

    model_config = {"from_attributes": True}
