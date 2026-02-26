import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CustomDomainCreate(BaseModel):
    domain: str = Field(..., max_length=255)
    domain_type: str


class CustomDomainResponse(BaseModel):
    domain_id: uuid.UUID
    gym_id: uuid.UUID
    domain: str
    domain_type: str
    status: str
    dns_records: dict | None = None
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
