import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.client import ClientResponse
from gym_api.schemas.trainer import TrainerCreate, TrainerResponse, TrainerUpdate
from gym_api.services import trainer_client_service, trainer_service

router = APIRouter(prefix="/v1/trainers", tags=["trainers"])


@router.post("", status_code=201, response_model=dict)
async def create_trainer(
    body: TrainerCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    trainer = await trainer_service.create_trainer(db, gym_id=gym_id, **body.model_dump())
    return {"data": TrainerResponse.model_validate(trainer)}


@router.get("", response_model=dict)
async def list_trainers(
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await trainer_service.list_trainers(db, gym_id, cursor=cursor, limit=limit)
    return {
        "data": [TrainerResponse.model_validate(t) for t in items],
        "pagination": pagination,
    }


@router.get("/{trainer_id}", response_model=dict)
async def get_trainer(
    trainer_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    trainer = await trainer_service.get_trainer(db, gym_id, trainer_id)
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return {"data": TrainerResponse.model_validate(trainer)}


@router.patch("/{trainer_id}", response_model=dict)
async def update_trainer(
    trainer_id: uuid.UUID,
    body: TrainerUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    trainer = await trainer_service.get_trainer(db, gym_id, trainer_id)
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    trainer = await trainer_service.update_trainer(
        db, trainer, **body.model_dump(exclude_unset=True)
    )
    return {"data": TrainerResponse.model_validate(trainer)}


@router.get("/{trainer_id}/clients", response_model=dict)
async def list_trainer_clients(
    trainer_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await trainer_client_service.list_trainer_clients(
        db, gym_id, trainer_id, cursor=cursor, limit=limit
    )
    return {
        "data": [ClientResponse.model_validate(c) for c in items],
        "pagination": pagination,
    }
