import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AgreementTemplateCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    content: str
    requires_signature: bool = True
    extra_data: dict | None = None


class AgreementTemplateUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    content: str | None = None
    is_active: bool | None = None
    requires_signature: bool | None = None
    extra_data: dict | None = None


class AgreementTemplateResponse(BaseModel):
    agreement_template_id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    description: str | None = None
    content: str
    is_active: bool
    requires_signature: bool
    extra_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgreementSend(BaseModel):
    template_id: uuid.UUID
    client_id: uuid.UUID
    signer_email: str
    signer_name: str


class AgreementEnvelopeResponse(BaseModel):
    envelope_id: uuid.UUID
    gym_id: uuid.UUID
    template_id: uuid.UUID
    client_id: uuid.UUID
    status: str
    signer_email: str
    signer_name: str
    external_envelope_id: str | None = None
    provider: str | None = None
    signed_at: datetime | None = None
    expires_at: datetime | None = None
    signed_document_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
