import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.user import User
from gym_api.schemas.check_in import CheckInCreate, CheckInResponse, OccupancyResponse
from gym_api.services import check_in_service

router = APIRouter(tags=["check-ins"])


@router.post("/v1/check-ins", status_code=201, response_model=dict)
async def create_check_in(
    body: CheckInCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_in = await check_in_service.create_check_in(
        db,
        gym_id=gym_id,
        client_id=body.client_id,
        location_id=body.location_id,
        schedule_id=body.schedule_id,
        check_in_method=body.check_in_method or "manual",
        checked_in_by_user_id=user.user_id,
    )
    return {"data": CheckInResponse.model_validate(check_in)}


@router.get("/v1/check-ins", response_model=dict)
async def list_check_ins(
    location_id: uuid.UUID | None = Query(None),
    date: datetime | None = Query(None),
    client_id: uuid.UUID | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await check_in_service.list_check_ins(
        db, gym_id, location_id=location_id, date=date, client_id=client_id,
        cursor=cursor, limit=limit,
    )
    return {
        "data": [CheckInResponse.model_validate(ci) for ci in items],
        "pagination": pagination,
    }


@router.get("/v1/check-ins/{check_in_id}", response_model=dict)
async def get_check_in(
    check_in_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    check_in = await check_in_service.get_check_in(db, gym_id, check_in_id)
    if not check_in:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return {"data": CheckInResponse.model_validate(check_in)}


@router.post("/v1/check-ins/{check_in_id}/checkout", response_model=dict)
async def checkout(
    check_in_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    check_in = await check_in_service.get_check_in(db, gym_id, check_in_id)
    if not check_in:
        raise HTTPException(status_code=404, detail="Check-in not found")
    check_in = await check_in_service.checkout(db, check_in)
    return {"data": CheckInResponse.model_validate(check_in)}


@router.get("/v1/locations/{location_id}/occupancy", response_model=dict)
async def get_occupancy(
    location_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    count = await check_in_service.get_active_occupancy(db, gym_id, location_id)
    return {"data": OccupancyResponse(location_id=location_id, active_count=count)}
