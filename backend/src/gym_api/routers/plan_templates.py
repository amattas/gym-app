import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.plan_template import (
    PlanTemplateCreate,
    PlanTemplateResponse,
    PlanTemplateUpdate,
)
from gym_api.services import plan_template_service

router = APIRouter(prefix="/v1/plan-templates", tags=["plan-templates"])


@router.post("", status_code=201, response_model=dict)
async def create_plan_template(
    body: PlanTemplateCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await plan_template_service.create_plan_template(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": PlanTemplateResponse.model_validate(template)}


@router.get("", response_model=dict)
async def list_plan_templates(
    status: str | None = Query(None),
    plan_type: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await plan_template_service.list_plan_templates(
        db, gym_id, status=status, plan_type=plan_type, cursor=cursor, limit=limit
    )
    return {
        "data": [PlanTemplateResponse.model_validate(t) for t in items],
        "pagination": pagination,
    }


@router.get("/{plan_template_id}", response_model=dict)
async def get_plan_template(
    plan_template_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await plan_template_service.get_plan_template(db, gym_id, plan_template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plan template not found")
    return {"data": PlanTemplateResponse.model_validate(template)}


@router.patch("/{plan_template_id}", response_model=dict)
async def update_plan_template(
    plan_template_id: uuid.UUID,
    body: PlanTemplateUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await plan_template_service.get_plan_template(db, gym_id, plan_template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plan template not found")
    template = await plan_template_service.update_plan_template(
        db, template, **body.model_dump(exclude_unset=True)
    )
    return {"data": PlanTemplateResponse.model_validate(template)}


@router.delete("/{plan_template_id}", status_code=204)
async def delete_plan_template(
    plan_template_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    template = await plan_template_service.get_plan_template(db, gym_id, plan_template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Plan template not found")
    await plan_template_service.delete_plan_template(db, template)
