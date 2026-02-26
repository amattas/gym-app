import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.membership import (
    EntitlementResponse,
    MembershipCancel,
    MembershipCreate,
    MembershipPause,
    MembershipResponse,
    RecordVisitRequest,
)
from gym_api.services import membership_service

router = APIRouter(tags=["memberships"])


@router.post("/v1/clients/{client_id}/memberships", status_code=201, response_model=dict)
async def create_membership(
    client_id: uuid.UUID,
    body: MembershipCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    try:
        membership = await membership_service.create_membership(
            db,
            gym_id=gym_id,
            client_id=client_id,
            plan_template_id=body.plan_template_id,
            started_at=body.started_at,
            base_membership_id=body.base_membership_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": MembershipResponse.model_validate(membership)}


@router.get("/v1/memberships", response_model=dict)
async def list_gym_memberships(
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await membership_service.list_gym_memberships(
        db, gym_id, status=status, cursor=cursor, limit=limit
    )
    return {
        "data": [MembershipResponse.model_validate(m) for m in items],
        "pagination": pagination,
    }


@router.get("/v1/clients/{client_id}/memberships", response_model=dict)
async def list_client_memberships(
    client_id: uuid.UUID,
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await membership_service.list_client_memberships(
        db, gym_id, client_id, status=status, cursor=cursor, limit=limit
    )
    return {
        "data": [MembershipResponse.model_validate(m) for m in items],
        "pagination": pagination,
    }


@router.get("/v1/memberships/{membership_id}", response_model=dict)
async def get_membership(
    membership_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"data": MembershipResponse.model_validate(membership)}


@router.post("/v1/memberships/{membership_id}/pause", response_model=dict)
async def pause_membership(
    membership_id: uuid.UUID,
    body: MembershipPause | None = None,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    try:
        membership = await membership_service.pause_membership(
            db, membership, reason=body.reason if body else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": MembershipResponse.model_validate(membership)}


@router.post("/v1/memberships/{membership_id}/unpause", response_model=dict)
async def unpause_membership(
    membership_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    try:
        membership = await membership_service.unpause_membership(db, membership)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": MembershipResponse.model_validate(membership)}


@router.post("/v1/memberships/{membership_id}/cancel", response_model=dict)
async def cancel_membership(
    membership_id: uuid.UUID,
    body: MembershipCancel | None = None,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    try:
        membership = await membership_service.cancel_membership(
            db,
            membership,
            reason=body.reason if body else None,
            cancel_immediately=body.cancel_immediately if body else False,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": MembershipResponse.model_validate(membership)}


@router.get("/v1/memberships/{membership_id}/entitlements", response_model=dict)
async def get_entitlements(
    membership_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"data": EntitlementResponse.model_validate(membership)}


@router.post("/v1/memberships/{membership_id}/record-visit", response_model=dict)
async def record_visit(
    membership_id: uuid.UUID,
    body: RecordVisitRequest,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    membership = await membership_service.get_membership(db, gym_id, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    try:
        membership = await membership_service.record_visit(
            db, membership, notes=body.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": MembershipResponse.model_validate(membership)}
