import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.analytics import (
    MeasurementTrendPoint,
    VolumeTrendPoint,
    WorkoutStats,
)
from gym_api.schemas.personal_record import PersonalRecordResponse
from gym_api.services import analytics_service, pr_service, workout_service
from gym_api.services.analytics_service import compute_workout_analytics

router = APIRouter(prefix="/v1", tags=["analytics"])


@router.get("/workouts/{workout_id}/analytics/preview", response_model=dict)
async def workout_analytics_preview(
    workout_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    workout = await workout_service.get_workout(db, gym_id, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    exercises = await workout_service.list_workout_exercises(db, workout_id)
    sets_by_exercise = {}
    for ex in exercises:
        sets = await workout_service.list_sets(db, ex.workout_exercise_id)
        sets_by_exercise[str(ex.workout_exercise_id)] = [
            {
                "weight_kg": float(s.weight_kg) if s.weight_kg else None,
                "reps": s.reps,
                "completed": s.completed,
            }
            for s in sets
        ]

    exercises_data = [
        {
            "workout_exercise_id": str(ex.workout_exercise_id),
            "exercise_id": str(ex.exercise_id),
            "order_index": ex.order_index,
        }
        for ex in exercises
    ]

    analytics = compute_workout_analytics(exercises_data, sets_by_exercise)
    return {"data": analytics}


@router.get("/clients/{client_id}/personal-records", response_model=dict)
async def list_personal_records(
    client_id: uuid.UUID,
    exercise_id: uuid.UUID | None = Query(None),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    records = await pr_service.list_prs(
        db, client_id, exercise_id=exercise_id
    )
    return {
        "data": [
            PersonalRecordResponse.model_validate(r) for r in records
        ]
    }


@router.get(
    "/clients/{client_id}/analytics/workouts", response_model=dict
)
async def client_workout_stats(
    client_id: uuid.UUID,
    days: int = Query(30, ge=1, le=365),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    stats = await analytics_service.get_client_workout_stats(
        db, client_id=client_id, gym_id=gym_id, days=days
    )
    return {"data": WorkoutStats(**stats)}


@router.get(
    "/clients/{client_id}/analytics/volume", response_model=dict
)
async def client_volume_trend(
    client_id: uuid.UUID,
    days: int = Query(30, ge=1, le=365),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    trend = await analytics_service.get_client_volume_trend(
        db, client_id=client_id, gym_id=gym_id, days=days
    )
    return {"data": [VolumeTrendPoint(**p) for p in trend]}


@router.get(
    "/clients/{client_id}/analytics/measurements",
    response_model=dict,
)
async def client_measurement_trend(
    client_id: uuid.UUID,
    type: str = Query(...),
    days: int = Query(90, ge=1, le=365),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    trend = await analytics_service.get_client_measurement_trend(
        db,
        client_id=client_id,
        measurement_type=type,
        days=days,
    )
    return {"data": [MeasurementTrendPoint(**p) for p in trend]}


