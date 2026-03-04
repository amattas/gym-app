import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.schedule import ScheduleStatus
from gym_api.models.user import User
from gym_api.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    TrainerAvailabilityEntry,
    TrainerAvailabilityResponse,
    TrainerExceptionCreate,
    TrainerExceptionResponse,
)
from gym_api.services import schedule_service

router = APIRouter(tags=["schedules"])


@router.post("/v1/schedules", status_code=201, response_model=dict)
async def create_schedule(
    body: ScheduleCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        schedule = await schedule_service.create_schedule(
            db, gym_id=gym_id, created_by_user_id=user.user_id, **body.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.get("/v1/schedules", response_model=dict)
async def list_schedules(
    trainer_id: uuid.UUID | None = Query(None),
    client_id: uuid.UUID | None = Query(None),
    date: datetime | None = Query(None),
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await schedule_service.list_schedules(
        db, gym_id, trainer_id=trainer_id, client_id=client_id,
        date=date, status=status, cursor=cursor, limit=limit,
    )
    return {
        "data": [ScheduleResponse.model_validate(s) for s in items],
        "pagination": pagination,
    }


@router.get("/v1/schedules/{schedule_id}", response_model=dict)
async def get_schedule(
    schedule_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.patch("/v1/schedules/{schedule_id}", response_model=dict)
async def update_schedule(
    schedule_id: uuid.UUID,
    body: ScheduleUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule = await schedule_service.update_schedule(
        db, schedule, **body.model_dump(exclude_unset=True)
    )
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.post("/v1/schedules/{schedule_id}/cancel", response_model=dict)
async def cancel_schedule(
    schedule_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule = await schedule_service.update_schedule_status(
        db, schedule, status=ScheduleStatus.canceled
    )
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.post("/v1/schedules/{schedule_id}/confirm", response_model=dict)
async def confirm_schedule(
    schedule_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule = await schedule_service.update_schedule_status(
        db, schedule, status=ScheduleStatus.confirmed
    )
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.post("/v1/schedules/{schedule_id}/no-show", response_model=dict)
async def mark_no_show(
    schedule_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule = await schedule_service.update_schedule_status(
        db, schedule, status=ScheduleStatus.no_show
    )
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.post("/v1/schedules/{schedule_id}/complete", response_model=dict)
async def complete_schedule(
    schedule_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    schedule = await schedule_service.get_schedule(db, gym_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule = await schedule_service.update_schedule_status(
        db, schedule, status=ScheduleStatus.completed
    )
    return {"data": ScheduleResponse.model_validate(schedule)}


@router.get("/v1/trainers/{trainer_id}/availability", response_model=dict)
async def get_trainer_availability(
    trainer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    entries = await schedule_service.get_trainer_availability(db, trainer_id)
    return {"data": [TrainerAvailabilityResponse.model_validate(e) for e in entries]}


@router.put("/v1/trainers/{trainer_id}/availability", response_model=dict)
async def set_trainer_availability(
    trainer_id: uuid.UUID,
    body: list[TrainerAvailabilityEntry],
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    entries = await schedule_service.set_trainer_availability(
        db, trainer_id, [e.model_dump() for e in body]
    )
    return {"data": [TrainerAvailabilityResponse.model_validate(e) for e in entries]}


@router.post("/v1/trainers/{trainer_id}/exceptions", status_code=201, response_model=dict)
async def create_trainer_exception(
    trainer_id: uuid.UUID,
    body: TrainerExceptionCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    exc = await schedule_service.create_trainer_exception(
        db, trainer_id=trainer_id, **body.model_dump()
    )
    return {"data": TrainerExceptionResponse.model_validate(exc)}


@router.delete("/v1/trainer-exceptions/{exception_id}", status_code=204)
async def delete_trainer_exception(
    exception_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    exc = await schedule_service.get_trainer_exception(db, exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    await schedule_service.delete_trainer_exception(db, exc)
