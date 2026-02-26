import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.models.client_membership import ClientMembership, MembershipStatus
from gym_api.models.invoice import Invoice, InvoiceStatus
from gym_api.models.stripe_account import StripeAccount
from gym_api.services import stripe_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.json()
    event_type = body.get("type", "")
    data_obj = body.get("data", {}).get("object", {})

    if event_type == "account.updated":
        stripe_connect_id = data_obj.get("id")
        if stripe_connect_id:
            result = await db.execute(
                select(StripeAccount).where(
                    StripeAccount.stripe_connect_id == stripe_connect_id
                )
            )
            account = result.scalar_one_or_none()
            if account:
                account.charges_enabled = data_obj.get(
                    "charges_enabled", account.charges_enabled
                )
                account.payouts_enabled = data_obj.get(
                    "payouts_enabled", account.payouts_enabled
                )
                await db.commit()
                logger.info(
                    "Updated StripeAccount %s", stripe_connect_id
                )

    elif event_type == "payment_intent.succeeded":
        payment_id = data_obj.get("metadata", {}).get("payment_id")
        if payment_id:
            await stripe_service.handle_payment_success(
                db, payment_id=payment_id
            )
            logger.info("Payment succeeded: %s", payment_id)

    elif event_type == "payment_intent.payment_failed":
        payment_id = data_obj.get("metadata", {}).get("payment_id")
        reason = (
            data_obj.get("last_payment_error", {}).get("message")
            or "unknown"
        )
        if payment_id:
            await stripe_service.handle_payment_failure(
                db, payment_id=payment_id, reason=reason
            )
            logger.info("Payment failed: %s", payment_id)

    elif event_type == "invoice.paid":
        stripe_invoice_id = data_obj.get("id")
        if stripe_invoice_id:
            result = await db.execute(
                select(Invoice).where(
                    Invoice.stripe_invoice_id == stripe_invoice_id
                )
            )
            invoice = result.scalar_one_or_none()
            if invoice:
                invoice.status = InvoiceStatus.paid
                await db.commit()
                logger.info(
                    "Invoice paid: %s", stripe_invoice_id
                )

    elif event_type == "invoice.payment_failed":
        stripe_invoice_id = data_obj.get("id")
        if stripe_invoice_id:
            result = await db.execute(
                select(Invoice).where(
                    Invoice.stripe_invoice_id == stripe_invoice_id
                )
            )
            invoice = result.scalar_one_or_none()
            if invoice:
                invoice.status = InvoiceStatus.uncollectible
                await db.commit()
                logger.info(
                    "Invoice payment failed: %s", stripe_invoice_id
                )

    elif event_type == "customer.subscription.updated":
        logger.info("Subscription updated event received")

    elif event_type == "customer.subscription.deleted":
        subscription_id = data_obj.get("id")
        membership_id = (
            data_obj.get("metadata", {}).get("membership_id")
        )
        if membership_id:
            result = await db.execute(
                select(ClientMembership).where(
                    ClientMembership.client_membership_id
                    == membership_id
                )
            )
            membership = result.scalar_one_or_none()
            if membership:
                membership.status = MembershipStatus.cancelled
                await db.commit()
                logger.info(
                    "Membership cancelled via subscription %s",
                    subscription_id,
                )

    return {"received": True}
