from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def handle_stripe_webhook(request: Request):
    body = await request.json()
    event_type = body.get("type", "")

    if event_type == "account.updated":
        pass
    elif event_type == "payment_intent.succeeded":
        pass
    elif event_type == "payment_intent.payment_failed":
        pass
    elif event_type == "invoice.paid":
        pass
    elif event_type == "invoice.payment_failed":
        pass
    elif event_type == "customer.subscription.updated":
        pass
    elif event_type == "customer.subscription.deleted":
        pass

    return {"received": True}
