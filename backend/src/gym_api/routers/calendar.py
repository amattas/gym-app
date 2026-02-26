import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.services import busyness_service, ical_service, reporting_service

router = APIRouter(tags=["calendar"])


@router.get("/v1/locations/{location_id}/busyness", response_model=dict)
async def get_location_busyness(
    location_id: uuid.UUID,
    date: datetime = Query(...),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    slots = await busyness_service.get_location_busyness(db, gym_id, location_id, date)
    return {"data": slots}


@router.get("/v1/trainers/{trainer_id}/busyness", response_model=dict)
async def get_trainer_busyness(
    trainer_id: uuid.UUID,
    date: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
):
    slots = await busyness_service.get_trainer_busyness(db, trainer_id, date)
    return {"data": slots}


@router.post("/v1/trainers/{trainer_id}/calendar/token/generate", response_model=dict)
async def generate_trainer_calendar_token(
    trainer_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    cal_token, raw_token = await ical_service.generate_token(
        db, gym_id=gym_id, owner_type="trainer", owner_id=trainer_id
    )
    return {"data": {"token": raw_token, "token_id": str(cal_token.token_id)}}


@router.get("/v1/trainers/{trainer_id}/calendar.ics")
async def get_trainer_ics(
    trainer_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    cal_token = await ical_service.validate_token(db, token)
    if not cal_token or cal_token.owner_id != trainer_id:
        raise HTTPException(status_code=401, detail="Invalid calendar token")
    ics_content = await ical_service.generate_ics(db, "trainer", trainer_id)
    return PlainTextResponse(ics_content, media_type="text/calendar")


@router.post("/v1/trainers/{trainer_id}/calendar/token/rotate", response_model=dict)
async def rotate_trainer_calendar_token(
    trainer_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    cal_token, raw_token = await ical_service.generate_token(
        db, gym_id=gym_id, owner_type="trainer", owner_id=trainer_id
    )
    return {"data": {"token": raw_token, "token_id": str(cal_token.token_id)}}


@router.post("/v1/clients/{client_id}/calendar/token/generate", response_model=dict)
async def generate_client_calendar_token(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    cal_token, raw_token = await ical_service.generate_token(
        db, gym_id=gym_id, owner_type="client", owner_id=client_id
    )
    return {"data": {"token": raw_token, "token_id": str(cal_token.token_id)}}


@router.get("/v1/clients/{client_id}/calendar.ics")
async def get_client_ics(
    client_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    cal_token = await ical_service.validate_token(db, token)
    if not cal_token or cal_token.owner_id != client_id:
        raise HTTPException(status_code=401, detail="Invalid calendar token")
    ics_content = await ical_service.generate_ics(db, "client", client_id)
    return PlainTextResponse(ics_content, media_type="text/calendar")


@router.get("/v1/gyms/{gym_id}/analytics/dashboard", response_model=dict)
async def get_dashboard(
    gym_id: uuid.UUID,
    period: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    data = await reporting_service.get_gym_dashboard(db, gym_id, period_days=period)
    return {"data": data}


@router.get("/v1/gyms/{gym_id}/analytics/trainers", response_model=dict)
async def get_trainer_analytics(
    gym_id: uuid.UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    data = await reporting_service.get_trainer_utilization(
        db, gym_id, start_date=start_date, end_date=end_date
    )
    return {"data": data}


@router.get("/v1/clients/{client_id}/adherence", response_model=dict)
async def get_client_adherence(
    client_id: uuid.UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    data = await reporting_service.get_client_adherence(
        db, gym_id, client_id, start_date=start_date, end_date=end_date
    )
    return {"data": data}
