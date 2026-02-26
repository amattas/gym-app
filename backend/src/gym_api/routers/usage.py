import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.usage import UsageMetricResponse
from gym_api.services import usage_metering_service

router = APIRouter(prefix="/v1/usage", tags=["usage"])


@router.get("", response_model=dict)
async def get_usage(
    period_start: datetime | None = Query(None),
    period_end: datetime | None = Query(None),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    metrics = await usage_metering_service.get_usage_summary(
        db, gym_id, period_start=period_start, period_end=period_end
    )
    return {
        "data": [UsageMetricResponse.model_validate(m) for m in metrics],
    }


@router.get("/totals", response_model=dict)
async def get_usage_totals(
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    totals = await usage_metering_service.get_metric_totals(db, gym_id)
    return {"data": totals}


@router.get("/check/{metric_name}", response_model=dict)
async def check_usage_limit(
    metric_name: str,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await usage_metering_service.check_limit(
        db, gym_id, metric_name=metric_name
    )
    return {"data": result}
