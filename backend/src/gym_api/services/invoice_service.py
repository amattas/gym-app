import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.invoice import Invoice, Payment


async def get_invoice(
    db: AsyncSession, gym_id: uuid.UUID, invoice_id: uuid.UUID
) -> Invoice | None:
    result = await db.execute(
        select(Invoice).where(
            Invoice.invoice_id == invoice_id, Invoice.gym_id == gym_id
        )
    )
    return result.scalar_one_or_none()


async def list_invoices_for_membership(
    db: AsyncSession, gym_id: uuid.UUID, membership_id: uuid.UUID
) -> list[Invoice]:
    result = await db.execute(
        select(Invoice)
        .where(Invoice.gym_id == gym_id, Invoice.membership_id == membership_id)
        .order_by(Invoice.created_at.desc())
    )
    return list(result.scalars().all())


async def list_payments_for_membership(
    db: AsyncSession, gym_id: uuid.UUID, membership_id: uuid.UUID
) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .join(Invoice, Payment.invoice_id == Invoice.invoice_id)
        .where(Invoice.gym_id == gym_id, Invoice.membership_id == membership_id)
        .order_by(Payment.created_at.desc())
    )
    return list(result.scalars().all())
