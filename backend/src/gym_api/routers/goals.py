import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.client_program import (
    ClientProgramCreate,
    ClientProgramResponse,
    ProgramDayCreate,
    ProgramDayExerciseCreate,
    ProgramDayExerciseResponse,
    ProgramDayResponse,
)
from gym_api.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from gym_api.services import client_program_service, goal_service

router = APIRouter(tags=["goals"])


@router.post("/v1/clients/{client_id}/goals", status_code=201, response_model=dict)
async def create_goal(
    client_id: uuid.UUID,
    body: GoalCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    goal = await goal_service.create_goal(
        db, gym_id=gym_id, client_id=client_id, **body.model_dump()
    )
    return {"data": GoalResponse.model_validate(goal)}


@router.get("/v1/clients/{client_id}/goals", response_model=dict)
async def list_goals(
    client_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await goal_service.list_client_goals(
        db, gym_id, client_id, cursor=cursor, limit=limit
    )
    return {
        "data": [GoalResponse.model_validate(g) for g in items],
        "pagination": pagination,
    }


@router.get("/v1/goals/{goal_id}", response_model=dict)
async def get_goal(
    goal_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    goal = await goal_service.get_goal(db, gym_id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"data": GoalResponse.model_validate(goal)}


@router.put("/v1/goals/{goal_id}", response_model=dict)
async def update_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    goal = await goal_service.get_goal(db, gym_id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal = await goal_service.update_goal(db, goal, **body.model_dump(exclude_unset=True))
    return {"data": GoalResponse.model_validate(goal)}


@router.delete("/v1/goals/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    goal = await goal_service.get_goal(db, gym_id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    await goal_service.delete_goal(db, goal)


@router.post("/v1/clients/{client_id}/programs", status_code=201, response_model=dict)
async def assign_program(
    client_id: uuid.UUID,
    body: ClientProgramCreate,
    db: AsyncSession = Depends(get_db),
):
    cp = await client_program_service.assign_program(
        db, client_id=client_id, **body.model_dump()
    )
    return {"data": ClientProgramResponse.model_validate(cp)}


@router.get("/v1/clients/{client_id}/programs", response_model=dict)
async def list_client_programs(
    client_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await client_program_service.list_client_programs(
        db, client_id, cursor=cursor, limit=limit
    )
    return {
        "data": [ClientProgramResponse.model_validate(cp) for cp in items],
        "pagination": pagination,
    }


@router.get("/v1/programs/{program_id}/days", response_model=dict)
async def list_program_days(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    items = await client_program_service.list_program_days(db, program_id)
    return {"data": [ProgramDayResponse.model_validate(d) for d in items]}


@router.post("/v1/programs/{program_id}/days", status_code=201, response_model=dict)
async def create_program_day(
    program_id: uuid.UUID,
    body: ProgramDayCreate,
    db: AsyncSession = Depends(get_db),
):
    day = await client_program_service.create_program_day(
        db, program_id=program_id, **body.model_dump()
    )
    return {"data": ProgramDayResponse.model_validate(day)}


@router.get("/v1/program-days/{program_day_id}/exercises", response_model=dict)
async def list_program_day_exercises(
    program_day_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    items = await client_program_service.list_program_day_exercises(db, program_day_id)
    return {"data": [ProgramDayExerciseResponse.model_validate(e) for e in items]}


@router.post("/v1/program-days/{program_day_id}/exercises", status_code=201, response_model=dict)
async def create_program_day_exercise(
    program_day_id: uuid.UUID,
    body: ProgramDayExerciseCreate,
    db: AsyncSession = Depends(get_db),
):
    exercise = await client_program_service.create_program_day_exercise(
        db, program_day_id=program_day_id, **body.model_dump()
    )
    return {"data": ProgramDayExerciseResponse.model_validate(exercise)}
