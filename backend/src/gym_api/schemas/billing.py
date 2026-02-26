import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class StripeConnectCreate(BaseModel):
    return_url: str
    refresh_url: str


class StripeConnectResponse(BaseModel):
    stripe_account_id: uuid.UUID
    gym_id: uuid.UUID
    stripe_connect_id: str | None = None
    onboarding_status: str
    charges_enabled: bool
    payouts_enabled: bool
    default_currency: str
    processing_fee_percentage: float | None = None
    pass_fees_to_client: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StripeOnboardingLink(BaseModel):
    url: str


class ProcessingFeeUpdate(BaseModel):
    processing_fee_percentage: float | None = Field(None, ge=0, le=30)
    pass_fees_to_client: bool | None = None


class PaymentMethodResponse(BaseModel):
    payment_method_id: uuid.UUID
    account_id: uuid.UUID
    stripe_payment_method_id: str
    type: str
    brand: str | None = None
    last4: str | None = None
    exp_month: int | None = None
    exp_year: int | None = None
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentMethodCreate(BaseModel):
    stripe_payment_method_id: str


class CheckoutCreate(BaseModel):
    membership_id: uuid.UUID
    payment_method_id: uuid.UUID | None = None
    discount_code: str | None = None


class SessionPackPurchase(BaseModel):
    plan_template_id: uuid.UUID
    client_id: uuid.UUID
    payment_method_id: uuid.UUID | None = None
    discount_code: str | None = None


class CheckoutResponse(BaseModel):
    invoice_id: uuid.UUID
    payment_id: uuid.UUID | None = None
    client_secret: str | None = None
    status: str
    total: int
    currency: str


class InvoiceResponse(BaseModel):
    invoice_id: uuid.UUID
    gym_id: uuid.UUID
    account_id: uuid.UUID
    membership_id: uuid.UUID | None = None
    stripe_invoice_id: str | None = None
    status: str
    subtotal: int
    discount_amount: int
    tax_amount: int
    processing_fee: int
    total: int
    currency: str
    description: str | None = None
    line_items: dict | None = None
    due_date: datetime | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    payment_id: uuid.UUID
    gym_id: uuid.UUID
    invoice_id: uuid.UUID | None = None
    account_id: uuid.UUID
    stripe_payment_intent_id: str | None = None
    amount: int
    currency: str
    status: str
    failure_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DiscountCodeCreate(BaseModel):
    code: str = Field(..., max_length=50)
    description: str | None = None
    discount_type: str
    amount: float = Field(..., gt=0)
    max_uses: int | None = None
    applicable_plan_types: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class DiscountCodeUpdate(BaseModel):
    description: str | None = None
    is_active: bool | None = None
    max_uses: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class DiscountCodeResponse(BaseModel):
    discount_code_id: uuid.UUID
    gym_id: uuid.UUID
    code: str
    description: str | None = None
    discount_type: str
    amount: float
    max_uses: int | None = None
    times_used: int
    applicable_plan_types: str | None = None
    is_active: bool
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrialConfig(BaseModel):
    trial_days: int = Field(..., ge=1, le=365)


class DiscountValidation(BaseModel):
    code: str
    plan_type: str | None = None


class DiscountValidationResponse(BaseModel):
    valid: bool
    discount_type: str | None = None
    amount: float | None = None
    message: str | None = None
