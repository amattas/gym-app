import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.workout import (
    WorkoutCreate,
    WorkoutExerciseCreate,
    WorkoutExerciseResponse,
    WorkoutResponse,
    WorkoutSetCreate,
    WorkoutSetResponse,
    WorkoutUpdate,
)
from gym_api.services import workout_service

router = APIRouter(prefix="/v1/workouts", tags=["workouts"])


@router.post("", status_code=201, response_model=dict)
async def create_workout(
    body: WorkoutCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.create_workout(db, gym_id=gym_id, **body.model_dump())
    return {"data": WorkoutResponse.model_validate(workout)}


@router.get("", response_model=dict)
async def list_workouts(
    client_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await workout_service.list_workouts(
        db, gym_id, client_id=client_id, status=status, cursor=cursor, limit=limit
    )
    return {
        "data": [WorkoutResponse.model_validate(w) for w in items],
        "pagination": pagination,
    }


@router.get("/{workout_id}", response_model=dict)
async def get_workout(
    workout_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"data": WorkoutResponse.model_validate(workout)}


@router.patch("/{workout_id}", response_model=dict)
async def update_workout(
    workout_id: uuid.UUID,
    body: WorkoutUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    workout = await workout_service.update_workout(
        db, workout, **body.model_dump(exclude_unset=True)
    )
    return {"data": WorkoutResponse.model_validate(workout)}


@router.post("/{workout_id}/exercises", status_code=201, response_model=dict)
async def add_exercise(
    workout_id: uuid.UUID,
    body: WorkoutExerciseCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    we = await workout_service.add_exercise_to_workout(
        db, workout_id=workout_id, **body.model_dump()
    )
    return {"data": WorkoutExerciseResponse.model_validate(we)}


@router.get("/{workout_id}/exercises", response_model=dict)
async def list_exercises(
    workout_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    items = await workout_service.list_workout_exercises(db, workout_id)
    return {"data": [WorkoutExerciseResponse.model_validate(we) for we in items]}


@router.post(
    "/{workout_id}/exercises/{workout_exercise_id}/sets",
    status_code=201,
    response_model=dict,
)
async def add_set(
    workout_id: uuid.UUID,
    workout_exercise_id: uuid.UUID,
    body: WorkoutSetCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    ws = await workout_service.add_set(
        db, workout_exercise_id=workout_exercise_id, **body.model_dump()
    )
    return {"data": WorkoutSetResponse.model_validate(ws)}


@router.get("/{workout_id}/exercises/{workout_exercise_id}/sets", response_model=dict)
async def list_sets(
    workout_id: uuid.UUID,
    workout_exercise_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    items = await workout_service.list_sets(db, workout_exercise_id)
    return {"data": [WorkoutSetResponse.model_validate(s) for s in items]}
