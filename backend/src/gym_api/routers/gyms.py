import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.cache.cache_service import cache_get, cache_set
from gym_api.database import get_db
from gym_api.dependencies.auth import require_role
from gym_api.models.user import User, UserRole
from gym_api.schemas.gym import GymCreate, GymResponse, GymUpdate
from gym_api.services import gym_service

router = APIRouter(prefix="/v1/gyms", tags=["gyms"])

CACHE_TTL = 300


@router.post("", status_code=201, response_model=dict)
async def create_gym(
    body: GymCreate,
    user: User = Depends(require_role(UserRole.platform_admin)),
    db: AsyncSession = Depends(get_db),
):
    try:
        gym = await gym_service.create_gym(db, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"data": GymResponse.model_validate(gym)}


@router.get("", response_model=dict)
async def list_gyms(
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_role(UserRole.platform_admin)),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await gym_service.list_gyms(db, cursor=cursor, limit=limit)
    return {
        "data": [GymResponse.model_validate(g) for g in items],
        "pagination": pagination,
    }


@router.get("/{gym_id}", response_model=dict)
async def get_gym(
    gym_id: uuid.UUID,
    user: User = Depends(require_role(UserRole.platform_admin, UserRole.gym_admin)),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"gym:{gym_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    gym = await gym_service.get_gym(db, gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    response = {"data": GymResponse.model_validate(gym).model_dump()}
    await cache_set(cache_key, response, CACHE_TTL)
    return response


@router.patch("/{gym_id}", response_model=dict)
async def update_gym(
    gym_id: uuid.UUID,
    body: GymUpdate,
    user: User = Depends(require_role(UserRole.platform_admin, UserRole.gym_admin)),
    db: AsyncSession = Depends(get_db),
):
    gym = await gym_service.get_gym(db, gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    gym = await gym_service.update_gym(db, gym, **body.model_dump(exclude_unset=True))
    return {"data": GymResponse.model_validate(gym)}
