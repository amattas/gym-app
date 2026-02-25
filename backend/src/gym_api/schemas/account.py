import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    account_type: str = "individual"
    billing_email: str | None = Field(None, max_length=255)
    billing_address: dict | None = None


class AccountResponse(BaseModel):
    account_id: uuid.UUID
    gym_id: uuid.UUID
    account_type: str
    billing_email: str | None = None
    billing_address: dict | None = None
    stripe_customer_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemberAdd(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str | None = Field(None, max_length=255)
    relationship_to_primary: str | None = Field(None, max_length=100)
