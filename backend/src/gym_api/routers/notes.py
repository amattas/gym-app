import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.user import User
from gym_api.services import note_service

router = APIRouter(tags=["notes"])


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    note_id: uuid.UUID
    gym_id: uuid.UUID
    notable_type: str
    notable_id: uuid.UUID
    author_user_id: uuid.UUID
    content: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


@router.post("/v1/clients/{client_id}/notes", status_code=201, response_model=dict)
async def create_client_note(
    client_id: uuid.UUID,
    body: NoteCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await note_service.create_note(
        db,
        gym_id=gym_id,
        notable_type="client",
        notable_id=client_id,
        author_user_id=user.user_id,
        content=body.content,
    )
    return {"data": NoteResponse.model_validate(note)}


@router.get("/v1/clients/{client_id}/notes", response_model=dict)
async def list_client_notes(
    client_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await note_service.list_notes(
        db, gym_id, "client", client_id, cursor=cursor, limit=limit
    )
    return {
        "data": [NoteResponse.model_validate(n) for n in items],
        "pagination": pagination,
    }


@router.post("/v1/workouts/{workout_id}/notes", status_code=201, response_model=dict)
async def create_workout_note(
    workout_id: uuid.UUID,
    body: NoteCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await note_service.create_note(
        db,
        gym_id=gym_id,
        notable_type="workout",
        notable_id=workout_id,
        author_user_id=user.user_id,
        content=body.content,
    )
    return {"data": NoteResponse.model_validate(note)}


@router.get("/v1/workouts/{workout_id}/notes", response_model=dict)
async def list_workout_notes(
    workout_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await note_service.list_notes(
        db, gym_id, "workout", workout_id, cursor=cursor, limit=limit
    )
    return {
        "data": [NoteResponse.model_validate(n) for n in items],
        "pagination": pagination,
    }


@router.put("/v1/notes/{note_id}", response_model=dict)
async def update_note(
    note_id: uuid.UUID,
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
):
    note = await note_service.update_note(
        db, note_id=note_id, content=body.content
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"data": NoteResponse.model_validate(note)}


@router.delete("/v1/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await note_service.delete_note(db, note_id=note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
