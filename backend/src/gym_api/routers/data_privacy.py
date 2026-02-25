import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.services import data_deletion_service, data_export_service

router = APIRouter(tags=["data-privacy"])


class ExportRequestResponse(BaseModel):
    export_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    status: str
    format: str
    download_url: str | None = None
    requested_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeletionRequestCreate(BaseModel):
    reason: str | None = Field(None, max_length=1000)


class DeletionRequestResponse(BaseModel):
    deletion_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    status: str
    reason: str | None = None
    requested_at: datetime
    scheduled_for: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


@router.post("/v1/clients/{client_id}/data-export", status_code=201, response_model=dict)
async def create_data_export(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    request = await data_export_service.create_export_request(
        db, gym_id=gym_id, client_id=client_id
    )
    return {"data": ExportRequestResponse.model_validate(request)}


@router.get("/v1/data-exports/{export_id}/status", response_model=dict)
async def get_export_status(
    export_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    request = await data_export_service.get_export_request(db, export_id)
    if not request:
        raise HTTPException(status_code=404, detail="Export request not found")
    return {"data": ExportRequestResponse.model_validate(request)}


@router.get("/v1/data-exports/{export_id}/download", response_model=dict)
async def download_export(
    export_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    request = await data_export_service.get_export_request(db, export_id)
    if not request:
        raise HTTPException(status_code=404, detail="Export request not found")
    if not request.download_url:
        raise HTTPException(status_code=400, detail="Export not ready for download")
    return {"data": {"download_url": request.download_url}}


@router.post("/v1/clients/{client_id}/request-deletion", status_code=201, response_model=dict)
async def request_deletion(
    client_id: uuid.UUID,
    body: DeletionRequestCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    request = await data_deletion_service.create_deletion_request(
        db, gym_id=gym_id, client_id=client_id, reason=body.reason
    )
    return {"data": DeletionRequestResponse.model_validate(request)}
