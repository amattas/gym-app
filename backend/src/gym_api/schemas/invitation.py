import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InvitationCreate(BaseModel):
    email: str = Field(..., max_length=255)


class InvitationResponse(BaseModel):
    invitation_id: uuid.UUID
    gym_id: uuid.UUID
    email: str
    expires_at: datetime
    is_used: bool

    model_config = {"from_attributes": True}


class InvitationAcceptRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
