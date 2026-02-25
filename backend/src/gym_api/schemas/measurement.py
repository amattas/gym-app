import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    client_id: uuid.UUID
    type: str
    value: float
    unit: str = Field(..., max_length=20)


class MeasurementResponse(BaseModel):
    measurement_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    type: str
    value: float
    unit: str
    bmi: float | None = None
    measured_at: datetime

    model_config = {"from_attributes": True}
