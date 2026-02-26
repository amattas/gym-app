import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.cache.cache_service import cache_get, cache_set
from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.program import ProgramCreate, ProgramResponse, ProgramUpdate
from gym_api.services import program_service

router = APIRouter(prefix="/v1/programs", tags=["programs"])

CACHE_TTL = 300


@router.post("", status_code=201, response_model=dict)
async def create_program(
    body: ProgramCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    program = await program_service.create_program(db, gym_id=gym_id, **body.model_dump())
    return {"data": ProgramResponse.model_validate(program)}


@router.get("", response_model=dict)
async def list_programs(
    template_scope: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    items, pagination = await program_service.list_programs(
        db, gym_id, template_scope=template_scope, cursor=cursor, limit=limit
    )
    return {
        "data": [ProgramResponse.model_validate(p) for p in items],
        "pagination": pagination,
    }


@router.get("/{program_id}", response_model=dict)
async def get_program(
    program_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cache_key = f"program:{program_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    program = await program_service.get_program(db, gym_id, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    response = {"data": ProgramResponse.model_validate(program).model_dump()}
    await cache_set(cache_key, response, CACHE_TTL)
    return response


@router.patch("/{program_id}", response_model=dict)
async def update_program(
    program_id: uuid.UUID,
    body: ProgramUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    program = await program_service.get_program(db, gym_id, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    program = await program_service.update_program(
        db, program, **body.model_dump(exclude_unset=True)
    )
    return {"data": ProgramResponse.model_validate(program)}


@router.delete("/{program_id}", status_code=204)
async def delete_program(
    program_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    program = await program_service.get_program(db, gym_id, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    await program_service.delete_program(db, program)
