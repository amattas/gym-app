import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from gym_api.services import location_service

router = APIRouter(prefix="/v1/gyms/{gym_id}/locations", tags=["locations"])
location_detail_router = APIRouter(prefix="/v1/locations", tags=["locations"])


@router.post("", status_code=201, response_model=dict)
async def create_location(
    gym_id: uuid.UUID,
    body: LocationCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    location = await location_service.create_location(db, gym_id=gym_id, **body.model_dump())
    return {"data": LocationResponse.model_validate(location)}


@router.get("", response_model=dict)
async def list_locations(
    gym_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await location_service.list_locations(
        db, gym_id, cursor=cursor, limit=limit
    )
    return {
        "data": [LocationResponse.model_validate(loc) for loc in items],
        "pagination": pagination,
    }


@location_detail_router.get("/{location_id}", response_model=dict)
async def get_location(
    location_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    location = await location_service.get_location(db, gym_id, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"data": LocationResponse.model_validate(location)}


@location_detail_router.put("/{location_id}", response_model=dict)
async def update_location(
    location_id: uuid.UUID,
    body: LocationUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    location = await location_service.get_location(db, gym_id, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    location = await location_service.update_location(
        db, location, **body.model_dump(exclude_unset=True)
    )
    return {"data": LocationResponse.model_validate(location)}


@location_detail_router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    location = await location_service.get_location(db, gym_id, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    await location_service.delete_location(db, location)
