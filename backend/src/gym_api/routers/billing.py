import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.client_membership import MembershipStatus
from gym_api.models.plan_template import PlanType
from gym_api.schemas.billing import (
    CheckoutCreate,
    DiscountCodeCreate,
    DiscountCodeResponse,
    DiscountCodeUpdate,
    DiscountValidation,
    DiscountValidationResponse,
    InvoiceResponse,
    PaymentMethodCreate,
    PaymentMethodResponse,
    PaymentResponse,
    ProcessingFeeUpdate,
    SessionPackPurchase,
    StripeConnectCreate,
    StripeConnectResponse,
)
from gym_api.services import (
    discount_service,
    invoice_service,
    membership_service,
    plan_template_service,
    stripe_service,
)

router = APIRouter(prefix="/v1/billing", tags=["billing"])


@router.post("/stripe/connect", status_code=201, response_model=dict)
async def create_stripe_connect(
    body: StripeConnectCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await stripe_service.create_onboarding_link(
        db, gym_id=gym_id, return_url=body.return_url, refresh_url=body.refresh_url
    )
    return {
        "data": StripeConnectResponse.model_validate(result["account"]),
        "onboarding_url": result["url"],
    }


@router.get("/stripe/account", response_model=dict)
async def get_stripe_account(
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    account = await stripe_service.get_stripe_account(db, gym_id)
    if not account:
        raise HTTPException(status_code=404, detail="Stripe account not found")
    return {"data": StripeConnectResponse.model_validate(account)}


@router.patch("/stripe/fees", response_model=dict)
async def update_processing_fees(
    body: ProcessingFeeUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    account = await stripe_service.get_stripe_account(db, gym_id)
    if not account:
        raise HTTPException(status_code=404, detail="Stripe account not found")
    account = await stripe_service.update_stripe_account(
        db, account, **body.model_dump(exclude_unset=True)
    )
    return {"data": StripeConnectResponse.model_validate(account)}


@router.post("/payment-methods", status_code=201, response_model=dict)
async def add_payment_method(
    body: PaymentMethodCreate,
    account_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    pm = await stripe_service.add_payment_method(
        db, account_id=account_id, **body.model_dump()
    )
    return {"data": PaymentMethodResponse.model_validate(pm)}


@router.get("/payment-methods", response_model=dict)
async def list_payment_methods(
    account_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    methods = await stripe_service.list_payment_methods(db, account_id)
    return {"data": [PaymentMethodResponse.model_validate(m) for m in methods]}


@router.delete("/payment-methods/{payment_method_id}", status_code=204)
async def remove_payment_method(
    payment_method_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    pm = await stripe_service.get_payment_method(db, payment_method_id)
    if not pm:
        raise HTTPException(status_code=404, detail="Payment method not found")
    await stripe_service.delete_payment_method(db, pm)


@router.post("/checkout", status_code=201, response_model=dict)
async def create_checkout(
    body: CheckoutCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    m = await membership_service.get_membership(db, gym_id, body.membership_id)
    if not m:
        raise HTTPException(status_code=404, detail="Membership not found")

    template = await plan_template_service.get_plan_template(db, gym_id, m.plan_template_id)
    payment_config = (template.payment_config or {}) if template else {}
    subtotal = payment_config.get("price_cents", 0)

    discount_amount = 0
    if body.discount_code:
        discount_amount, _ = await discount_service.apply_discount(
            db, gym_id, code_str=body.discount_code, subtotal=subtotal
        )

    result = await stripe_service.create_checkout(
        db,
        gym_id=gym_id,
        account_id=_user.user_id,
        membership_id=body.membership_id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        description=f"Payment for {template.name}" if template else "Membership checkout",
    )
    return {"data": result}


@router.post("/session-packs/purchase", status_code=201, response_model=dict)
async def purchase_session_pack(
    body: SessionPackPurchase,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await plan_template_service.get_plan_template(db, gym_id, body.plan_template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plan template not found")
    if template.plan_type not in (PlanType.session_pack, PlanType.punch_card):
        raise HTTPException(status_code=400, detail="Plan template is not a session pack")

    payment_config = template.payment_config or {}
    price_cents = payment_config.get("price_cents", 0)
    if price_cents <= 0:
        raise HTTPException(status_code=400, detail="Plan template has no price configured")

    try:
        m = await membership_service.create_membership(
            db,
            gym_id=gym_id,
            client_id=body.client_id,
            plan_template_id=body.plan_template_id,
            initial_status=MembershipStatus.pending,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    discount_amount = 0
    if body.discount_code:
        discount_amount, _ = await discount_service.apply_discount(
            db, gym_id, code_str=body.discount_code, subtotal=price_cents
        )

    result = await stripe_service.create_checkout(
        db,
        gym_id=gym_id,
        account_id=_user.user_id,
        membership_id=m.client_membership_id,
        subtotal=price_cents,
        discount_amount=discount_amount,
        description=f"Session pack: {template.name}",
    )
    result["membership_id"] = m.client_membership_id
    return {"data": result}


@router.get("/invoices", response_model=dict)
async def list_invoices(
    membership_id: uuid.UUID = Query(...),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    invoices = await invoice_service.list_invoices_for_membership(
        db, gym_id, membership_id
    )
    return {"data": [InvoiceResponse.model_validate(i) for i in invoices]}


@router.get("/invoices/{invoice_id}", response_model=dict)
async def get_invoice(
    invoice_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    invoice = await invoice_service.get_invoice(db, gym_id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"data": InvoiceResponse.model_validate(invoice)}


@router.get("/payments", response_model=dict)
async def list_payments(
    membership_id: uuid.UUID = Query(...),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    payments = await invoice_service.list_payments_for_membership(
        db, gym_id, membership_id
    )
    return {"data": [PaymentResponse.model_validate(p) for p in payments]}


@router.post("/discount-codes", status_code=201, response_model=dict)
async def create_discount_code(
    body: DiscountCodeCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    code = await discount_service.create_discount_code(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": DiscountCodeResponse.model_validate(code)}


@router.get("/discount-codes", response_model=dict)
async def list_discount_codes(
    is_active: bool | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await discount_service.list_discount_codes(
        db, gym_id, is_active=is_active, cursor=cursor, limit=limit
    )
    return {
        "data": [DiscountCodeResponse.model_validate(c) for c in items],
        "pagination": pagination,
    }


@router.get("/discount-codes/{discount_code_id}", response_model=dict)
async def get_discount_code(
    discount_code_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    code = await discount_service.get_discount_code(db, gym_id, discount_code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Discount code not found")
    return {"data": DiscountCodeResponse.model_validate(code)}


@router.patch("/discount-codes/{discount_code_id}", response_model=dict)
async def update_discount_code(
    discount_code_id: uuid.UUID,
    body: DiscountCodeUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    code = await discount_service.get_discount_code(db, gym_id, discount_code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Discount code not found")
    code = await discount_service.update_discount_code(
        db, code, **body.model_dump(exclude_unset=True)
    )
    return {"data": DiscountCodeResponse.model_validate(code)}


@router.delete("/discount-codes/{discount_code_id}", status_code=204)
async def delete_discount_code(
    discount_code_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    code = await discount_service.get_discount_code(db, gym_id, discount_code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Discount code not found")
    await discount_service.delete_discount_code(db, code)


@router.post("/discount-codes/validate", response_model=dict)
async def validate_discount_code(
    body: DiscountValidation,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await discount_service.validate_discount_code(
        db, gym_id, code_str=body.code, plan_type=body.plan_type
    )
    return {"data": DiscountValidationResponse(**result)}
