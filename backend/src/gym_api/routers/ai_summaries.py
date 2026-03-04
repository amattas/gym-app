import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.services import ai_summary_service

router = APIRouter(tags=["ai-summaries"])


class SummaryResponse(BaseModel):
    summary_id: uuid.UUID
    client_id: uuid.UUID
    gym_id: uuid.UUID
    content: str
    model_used: str | None = None
    generated_at: str
    is_stale: bool

    model_config = {"from_attributes": True}


class SummaryUpdate(BaseModel):
    content: str


@router.get("/v1/clients/{client_id}/ai-summary", response_model=dict)
async def get_client_summary(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    summary = await ai_summary_service.get_client_summary(db, gym_id, client_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No summary available")
    return {"data": SummaryResponse.model_validate(summary)}


@router.post("/v1/clients/{client_id}/ai-summary/regenerate", response_model=dict)
async def regenerate_summary(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    summary = await ai_summary_service.generate_client_summary(
        db, gym_id, client_id
    )
    return {"data": SummaryResponse.model_validate(summary)}


@router.put("/v1/ai-summaries/{summary_id}", response_model=dict)
async def update_summary(
    summary_id: uuid.UUID,
    body: SummaryUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    summary = await ai_summary_service.get_summary_by_id(db, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    summary = await ai_summary_service.update_summary(db, summary, content=body.content)
    return {"data": SummaryResponse.model_validate(summary)}
