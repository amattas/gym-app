import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.cache.cache_service import cache_get, cache_set
from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from gym_api.services import exercise_service

router = APIRouter(prefix="/v1/exercises", tags=["exercises"])

CACHE_TTL = 300


@router.post("", status_code=201, response_model=dict)
async def create_exercise(
    body: ExerciseCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    exercise = await exercise_service.create_exercise(db, gym_id=gym_id, **body.model_dump())
    return {"data": ExerciseResponse.model_validate(exercise)}


@router.get("", response_model=dict)
async def list_exercises(
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await exercise_service.list_exercises(
        db, gym_id, cursor=cursor, limit=limit
    )
    return {
        "data": [ExerciseResponse.model_validate(e) for e in items],
        "pagination": pagination,
    }


@router.get("/{exercise_id}", response_model=dict)
async def get_exercise(
    exercise_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cache_key = f"exercise:{exercise_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    exercise = await exercise_service.get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    # Ensure the exercise belongs to this gym or is global
    if exercise.gym_id is not None and exercise.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    response = {"data": ExerciseResponse.model_validate(exercise).model_dump()}
    await cache_set(cache_key, response, CACHE_TTL)
    return response


@router.patch("/{exercise_id}", response_model=dict)
async def update_exercise(
    exercise_id: uuid.UUID,
    body: ExerciseUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    exercise = await exercise_service.get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.gym_id is not None and exercise.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.gym_id is None:
        raise HTTPException(status_code=403, detail="Cannot modify global exercises")
    exercise = await exercise_service.update_exercise(
        db, exercise, **body.model_dump(exclude_unset=True)
    )
    return {"data": ExerciseResponse.model_validate(exercise)}


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    exercise = await exercise_service.get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.gym_id is not None and exercise.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.gym_id is None:
        raise HTTPException(status_code=403, detail="Cannot delete global exercises")
    await exercise_service.delete_exercise(db, exercise)
