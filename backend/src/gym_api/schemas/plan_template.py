import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PlanTemplateCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    plan_type: str
    status: str | None = None
    visit_entitlement: dict | None = None
    plan_duration: dict | None = None
    payment_config: dict | None = None
    modules_enabled: dict | None = None
    is_addon: bool = False
    requires_primary_plan_type: str | None = None
    addon_discount_percentage: float | None = None


class PlanTemplateUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    status: str | None = None
    visit_entitlement: dict | None = None
    plan_duration: dict | None = None
    payment_config: dict | None = None
    modules_enabled: dict | None = None
    is_addon: bool | None = None
    requires_primary_plan_type: str | None = None
    addon_discount_percentage: float | None = None


class PlanTemplateResponse(BaseModel):
    plan_template_id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    description: str | None = None
    plan_type: str
    status: str
    visit_entitlement: dict | None = None
    plan_duration: dict | None = None
    payment_config: dict | None = None
    modules_enabled: dict | None = None
    is_addon: bool
    requires_primary_plan_type: str | None = None
    addon_discount_percentage: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
