import uuid
from datetime import datetime

from pydantic import BaseModel


class UsageMetricResponse(BaseModel):
    rollup_id: uuid.UUID
    gym_id: uuid.UUID
    metric_name: str
    period_start: datetime
    period_end: datetime
    value: int
    limit_value: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UsageSummaryResponse(BaseModel):
    gym_id: uuid.UUID
    period_start: datetime
    period_end: datetime
    metrics: list[UsageMetricResponse]
