import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.agreement import (
    AgreementEnvelopeResponse,
    AgreementSend,
    AgreementTemplateCreate,
    AgreementTemplateResponse,
    AgreementTemplateUpdate,
)
from gym_api.services import esign_service

router = APIRouter(prefix="/v1/agreements", tags=["agreements"])


@router.post("/templates", status_code=201, response_model=dict)
async def create_template(
    body: AgreementTemplateCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await esign_service.create_template(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": AgreementTemplateResponse.model_validate(template)}


@router.get("/templates", response_model=dict)
async def list_templates(
    is_active: bool | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await esign_service.list_templates(
        db, gym_id, is_active=is_active, cursor=cursor, limit=limit
    )
    return {
        "data": [AgreementTemplateResponse.model_validate(t) for t in items],
        "pagination": pagination,
    }


@router.get("/templates/{template_id}", response_model=dict)
async def get_template(
    template_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await esign_service.get_template(db, gym_id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Agreement template not found")
    return {"data": AgreementTemplateResponse.model_validate(template)}


@router.patch("/templates/{template_id}", response_model=dict)
async def update_template(
    template_id: uuid.UUID,
    body: AgreementTemplateUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await esign_service.get_template(db, gym_id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Agreement template not found")
    template = await esign_service.update_template(
        db, template, **body.model_dump(exclude_unset=True)
    )
    return {"data": AgreementTemplateResponse.model_validate(template)}


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await esign_service.get_template(db, gym_id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Agreement template not found")
    await esign_service.delete_template(db, template)


@router.post("/send", status_code=201, response_model=dict)
async def send_agreement(
    body: AgreementSend,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    envelope = await esign_service.send_envelope(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": AgreementEnvelopeResponse.model_validate(envelope)}


@router.get("/envelopes", response_model=dict)
async def list_envelopes(
    client_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await esign_service.list_envelopes(
        db, gym_id, client_id=client_id, status=status, cursor=cursor, limit=limit
    )
    return {
        "data": [AgreementEnvelopeResponse.model_validate(e) for e in items],
        "pagination": pagination,
    }


@router.get("/envelopes/{envelope_id}", response_model=dict)
async def get_envelope(
    envelope_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    envelope = await esign_service.get_envelope(db, envelope_id)
    if not envelope:
        raise HTTPException(status_code=404, detail="Agreement envelope not found")
    return {"data": AgreementEnvelopeResponse.model_validate(envelope)}
