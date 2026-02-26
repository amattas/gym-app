import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.invoice import Invoice, InvoiceStatus, Payment, PaymentStatus
from gym_api.models.payment_method import PaymentMethod
from gym_api.models.stripe_account import OnboardingStatus, StripeAccount


async def get_or_create_stripe_account(
    db: AsyncSession, *, gym_id: uuid.UUID
) -> StripeAccount:
    result = await db.execute(
        select(StripeAccount).where(StripeAccount.gym_id == gym_id)
    )
    account = result.scalar_one_or_none()
    if account:
        return account
    account = StripeAccount(gym_id=gym_id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_stripe_account(
    db: AsyncSession, gym_id: uuid.UUID
) -> StripeAccount | None:
    result = await db.execute(
        select(StripeAccount).where(StripeAccount.gym_id == gym_id)
    )
    return result.scalar_one_or_none()


async def update_stripe_account(
    db: AsyncSession, account: StripeAccount, **kwargs
) -> StripeAccount:
    for key, value in kwargs.items():
        if value is not None:
            setattr(account, key, value)
    await db.commit()
    await db.refresh(account)
    return account


async def create_onboarding_link(
    db: AsyncSession, *, gym_id: uuid.UUID, return_url: str, refresh_url: str
) -> dict:
    account = await get_or_create_stripe_account(db, gym_id=gym_id)
    if not account.stripe_connect_id:
        account.stripe_connect_id = f"acct_placeholder_{uuid.uuid4().hex[:16]}"
        account.onboarding_status = OnboardingStatus.in_progress
        await db.commit()
        await db.refresh(account)
    return {
        "url": f"https://connect.stripe.com/setup/{account.stripe_connect_id}",
        "account": account,
    }


async def complete_onboarding(
    db: AsyncSession, *, gym_id: uuid.UUID
) -> StripeAccount:
    account = await get_or_create_stripe_account(db, gym_id=gym_id)
    account.onboarding_status = OnboardingStatus.complete
    account.charges_enabled = True
    account.payouts_enabled = True
    await db.commit()
    await db.refresh(account)
    return account


async def add_payment_method(
    db: AsyncSession, *, account_id: uuid.UUID, **kwargs
) -> PaymentMethod:
    pm = PaymentMethod(account_id=account_id, **kwargs)
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    return pm


async def list_payment_methods(
    db: AsyncSession, account_id: uuid.UUID
) -> list[PaymentMethod]:
    result = await db.execute(
        select(PaymentMethod)
        .where(PaymentMethod.account_id == account_id)
        .order_by(PaymentMethod.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_payment_method(db: AsyncSession, pm: PaymentMethod) -> None:
    await db.delete(pm)
    await db.commit()


async def get_payment_method(
    db: AsyncSession, payment_method_id: uuid.UUID
) -> PaymentMethod | None:
    result = await db.execute(
        select(PaymentMethod).where(
            PaymentMethod.payment_method_id == payment_method_id
        )
    )
    return result.scalar_one_or_none()


async def create_invoice(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Invoice:
    invoice = Invoice(gym_id=gym_id, **kwargs)
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def get_invoice(
    db: AsyncSession, gym_id: uuid.UUID, invoice_id: uuid.UUID
) -> Invoice | None:
    result = await db.execute(
        select(Invoice).where(
            Invoice.invoice_id == invoice_id, Invoice.gym_id == gym_id
        )
    )
    return result.scalar_one_or_none()


async def list_invoices(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    account_id: uuid.UUID | None = None,
    membership_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[Invoice]:
    query = select(Invoice).where(Invoice.gym_id == gym_id)
    if account_id:
        query = query.where(Invoice.account_id == account_id)
    if membership_id:
        query = query.where(Invoice.membership_id == membership_id)
    if status:
        query = query.where(Invoice.status == status)
    query = query.order_by(Invoice.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_invoice_status(
    db: AsyncSession, invoice: Invoice, *, status: InvoiceStatus
) -> Invoice:
    invoice.status = status
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def create_payment(db: AsyncSession, *, gym_id: uuid.UUID, **kwargs) -> Payment:
    payment = Payment(gym_id=gym_id, **kwargs)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def list_payments(
    db: AsyncSession, gym_id: uuid.UUID, *, membership_id: uuid.UUID | None = None
) -> list[Payment]:
    query = select(Payment).where(Payment.gym_id == gym_id)
    if membership_id:
        query = query.join(Invoice, Payment.invoice_id == Invoice.invoice_id).where(
            Invoice.membership_id == membership_id
        )
    query = query.order_by(Payment.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_checkout(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    account_id: uuid.UUID,
    membership_id: uuid.UUID,
    subtotal: int,
    discount_amount: int = 0,
    processing_fee: int = 0,
    description: str | None = None,
) -> dict:
    total = subtotal - discount_amount + processing_fee
    invoice = await create_invoice(
        db,
        gym_id=gym_id,
        account_id=account_id,
        membership_id=membership_id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        processing_fee=processing_fee,
        total=total,
        status=InvoiceStatus.open,
        description=description,
    )
    payment = await create_payment(
        db,
        gym_id=gym_id,
        account_id=account_id,
        invoice_id=invoice.invoice_id,
        amount=total,
        status=PaymentStatus.pending,
    )
    return {
        "invoice_id": invoice.invoice_id,
        "payment_id": payment.payment_id,
        "client_secret": f"pi_secret_{uuid.uuid4().hex[:16]}",
        "status": payment.status.value,
        "total": total,
        "currency": invoice.currency,
    }


async def handle_payment_success(
    db: AsyncSession, *, payment_id: uuid.UUID
) -> Payment | None:
    from gym_api.models.client_membership import ClientMembership, MembershipStatus

    result = await db.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        return None
    payment.status = PaymentStatus.succeeded
    if payment.invoice_id:
        inv_result = await db.execute(
            select(Invoice).where(Invoice.invoice_id == payment.invoice_id)
        )
        invoice = inv_result.scalar_one_or_none()
        if invoice:
            invoice.status = InvoiceStatus.paid
            if invoice.membership_id:
                m_result = await db.execute(
                    select(ClientMembership).where(
                        ClientMembership.client_membership_id == invoice.membership_id,
                        ClientMembership.status == MembershipStatus.pending,
                    )
                )
                membership = m_result.scalar_one_or_none()
                if membership:
                    membership.status = MembershipStatus.active
    await db.commit()
    await db.refresh(payment)
    return payment


async def handle_payment_failure(
    db: AsyncSession, *, payment_id: uuid.UUID, reason: str
) -> Payment | None:
    result = await db.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        return None
    payment.status = PaymentStatus.failed
    payment.failure_reason = reason
    await db.commit()
    await db.refresh(payment)
    return payment
