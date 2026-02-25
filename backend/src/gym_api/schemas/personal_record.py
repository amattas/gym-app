import uuid
from datetime import datetime

from pydantic import BaseModel


class PersonalRecordResponse(BaseModel):
    record_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    exercise_id: uuid.UUID
    pr_type: str
    weight_kg: float | None = None
    reps: int | None = None
    volume_kg: float | None = None
    exercise_name: str
    achieved_at: datetime

    model_config = {"from_attributes": True}
