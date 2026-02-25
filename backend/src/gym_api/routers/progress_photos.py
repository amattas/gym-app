import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.user import User
from gym_api.services import progress_photo_service

router = APIRouter(tags=["progress-photos"])


class ProgressPhotoCreate(BaseModel):
    storage_key: str = Field(..., max_length=500)
    content_type: str = Field(..., max_length=100)
    notes: str | None = None
    tags: dict | None = None
    measurement_id: uuid.UUID | None = None
    captured_at: datetime | None = None


class ProgressPhotoResponse(BaseModel):
    photo_id: uuid.UUID
    gym_id: uuid.UUID
    client_id: uuid.UUID
    storage_key: str
    content_type: str
    notes: str | None = None
    tags: dict | None = None
    measurement_id: uuid.UUID | None = None
    uploaded_by_user_id: uuid.UUID | None = None
    captured_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/v1/clients/{client_id}/progress-photos", status_code=201, response_model=dict)
async def create_progress_photo(
    client_id: uuid.UUID,
    body: ProgressPhotoCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    photo = await progress_photo_service.create_photo(
        db, gym_id=gym_id, client_id=client_id,
        uploaded_by_user_id=user.user_id, **body.model_dump()
    )
    return {"data": ProgressPhotoResponse.model_validate(photo)}


@router.get("/v1/clients/{client_id}/progress-photos", response_model=dict)
async def list_progress_photos(
    client_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await progress_photo_service.list_client_photos(
        db, gym_id, client_id, cursor=cursor, limit=limit
    )
    return {
        "data": [ProgressPhotoResponse.model_validate(p) for p in items],
        "pagination": pagination,
    }


@router.delete("/v1/progress-photos/{photo_id}", status_code=204)
async def delete_progress_photo(
    photo_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    photo = await progress_photo_service.get_photo(db, gym_id, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    await progress_photo_service.delete_photo(db, photo)
