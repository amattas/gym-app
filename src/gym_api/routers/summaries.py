import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from gym_api.config import settings
from gym_api.database import get_db
from gym_api.models.summary import ClientWorkoutSummary
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet
from gym_api.models.analytics import WorkoutAnalytics
from gym_api.models.client import Client
from gym_api.models.program import Program
from gym_api.services.ai.factory import create_summary_provider
from gym_api.services.ai.provider import SummaryGenerationError
from gym_api.services.summary_service import SummaryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/gyms/{gym_id}/clients/{client_id}", tags=["summaries"])

WORKOUT_HISTORY_LIMIT = 5


async def get_cached_summary(db: AsyncSession, client_id: uuid.UUID) -> ClientWorkoutSummary | None:
    result = await db.execute(
        select(ClientWorkoutSummary).where(ClientWorkoutSummary.client_id == client_id)
    )
    return result.scalar_one_or_none()


async def get_latest_workout_ended_at(db: AsyncSession, client_id: uuid.UUID) -> datetime | None:
    result = await db.execute(
        select(func.max(Workout.ended_at)).where(
            Workout.client_id == client_id,
            Workout.status == "completed",
        )
    )
    return result.scalar_one_or_none()


@router.get("/workout-summary")
async def get_workout_summary(
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add auth dependency when auth middleware is implemented
    # current_user: User = Depends(get_current_user),
):
    # Validate client belongs to gym
    client_result = await db.execute(select(Client).where(Client.client_id == client_id))
    client = client_result.scalar_one_or_none()
    if not client or client.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Client not found in this gym")

    cached = await get_cached_summary(db, client_id)
    latest_ended_at = await get_latest_workout_ended_at(db, client_id)

    if latest_ended_at is None:
        raise HTTPException(status_code=404, detail="No completed workouts found for this client")

    if cached and cached.generated_at >= latest_ended_at:
        return _format_response(cached, is_cached=True)

    workouts_result = await db.execute(
        select(Workout)
        .where(Workout.client_id == client_id, Workout.status == "completed")
        .options(
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.sets)
            .selectinload(WorkoutSet.measurements),
        )
        .order_by(Workout.ended_at.desc())
        .limit(WORKOUT_HISTORY_LIMIT)
    )
    workouts = list(workouts_result.scalars().all())

    if not workouts:
        raise HTTPException(status_code=404, detail="No completed workouts found for this client")

    workout_ids = [w.workout_id for w in workouts]
    analytics_result = await db.execute(
        select(WorkoutAnalytics).where(WorkoutAnalytics.workout_id.in_(workout_ids))
    )
    analytics = {a.workout_id: a for a in analytics_result.scalars().all()}

    client_name = f"{client.first_name} {client.last_name}"

    program_name = None
    if workouts[0].program_id:
        program_result = await db.execute(
            select(Program).where(Program.program_id == workouts[0].program_id)
        )
        program = program_result.scalar_one_or_none()
        program_name = program.name if program else None

    provider = create_summary_provider(
        settings.ai_summary_provider,
        api_key=settings.anthropic_api_key if settings.ai_summary_provider == "anthropic" else settings.openai_api_key,
        model=settings.ai_summary_model,
    )
    service = SummaryService(
        provider=provider,
        provider_name=settings.ai_summary_provider,
        model_id=settings.ai_summary_model,
    )

    try:
        summary = await service.get_summary(
            db=db,
            client_id=client_id,
            gym_id=gym_id,
            workouts=workouts,
            analytics=analytics,
            client_name=client_name,
            program_name=program_name,
            cached_summary=None,
        )
    except SummaryGenerationError:
        logger.exception("Failed to generate workout summary for client %s", client_id)
        raise HTTPException(status_code=503, detail="Summary generation temporarily unavailable")

    return _format_response(summary, is_cached=False)


def _format_response(summary: ClientWorkoutSummary, is_cached: bool) -> dict:
    return {
        "data": {
            "summary_id": str(summary.summary_id),
            "client_id": str(summary.client_id),
            "summary_text": summary.summary_text,
            "workouts_included": [str(w) for w in summary.workouts_included],
            "generated_at": summary.generated_at.isoformat(),
            "is_cached": is_cached,
        },
        "meta": {},
    }
