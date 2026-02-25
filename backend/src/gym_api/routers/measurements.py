import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.measurement import MeasurementCreate, MeasurementResponse
from gym_api.services import measurement_service

router = APIRouter(prefix="/v1/measurements", tags=["measurements"])


@router.post("", status_code=201, response_model=dict)
async def create_measurement(
    body: MeasurementCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    measurement = await measurement_service.create_measurement(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": MeasurementResponse.model_validate(measurement)}


@router.get("", response_model=dict)
async def list_measurements(
    client_id: uuid.UUID | None = Query(None),
    type: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await measurement_service.list_measurements(
        db, gym_id, client_id=client_id, type=type, cursor=cursor, limit=limit
    )
    return {
        "data": [MeasurementResponse.model_validate(m) for m in items],
        "pagination": pagination,
    }


@router.get("/{measurement_id}", response_model=dict)
async def get_measurement(
    measurement_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    measurement = await measurement_service.get_measurement(db, gym_id, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return {"data": MeasurementResponse.model_validate(measurement)}
