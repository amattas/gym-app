import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.services import webhook_endpoint_service

router = APIRouter(tags=["webhooks"])


class WebhookCreate(BaseModel):
    url: str = Field(..., max_length=2000)
    events: list[str] | None = None


class WebhookUpdate(BaseModel):
    url: str | None = Field(None, max_length=2000)
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookResponse(BaseModel):
    webhook_endpoint_id: uuid.UUID
    gym_id: uuid.UUID
    url: str
    events: list[str] | None = None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


@router.post("/v1/gyms/{gym_id}/webhooks", status_code=201, response_model=dict)
async def create_webhook(
    gym_id: uuid.UUID,
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
):
    webhook = await webhook_endpoint_service.create_webhook(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": WebhookResponse.model_validate(webhook)}


@router.get("/v1/gyms/{gym_id}/webhooks", response_model=dict)
async def list_webhooks(
    gym_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    items = await webhook_endpoint_service.list_webhooks(db, gym_id)
    return {"data": [WebhookResponse.model_validate(w) for w in items]}


@router.put("/v1/webhooks/{webhook_id}", response_model=dict)
async def update_webhook(
    webhook_id: uuid.UUID,
    body: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
):
    webhook = await webhook_endpoint_service.get_webhook(db, webhook_id, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    webhook = await webhook_endpoint_service.update_webhook(
        db, webhook, **body.model_dump(exclude_unset=True)
    )
    return {"data": WebhookResponse.model_validate(webhook)}


@router.delete("/v1/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    webhook = await webhook_endpoint_service.get_webhook(db, webhook_id, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await webhook_endpoint_service.delete_webhook(db, webhook)
