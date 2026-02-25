import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client_program import ClientProgram, ProgramDay, ProgramDayExercise
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def assign_program(
    db: AsyncSession, *, client_id: uuid.UUID, **kwargs
) -> ClientProgram:
    cp = ClientProgram(client_id=client_id, **kwargs)
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return cp


async def list_client_programs(
    db: AsyncSession,
    client_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[ClientProgram], dict]:
    query = select(ClientProgram).where(ClientProgram.client_id == client_id)
    query = apply_cursor_pagination(
        query, order_column=ClientProgram.assigned_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "assigned_at")
    return items, pagination


async def create_program_day(db: AsyncSession, *, program_id: uuid.UUID, **kwargs) -> ProgramDay:
    day = ProgramDay(program_id=program_id, **kwargs)
    db.add(day)
    await db.commit()
    await db.refresh(day)
    return day


async def list_program_days(
    db: AsyncSession, program_id: uuid.UUID
) -> list[ProgramDay]:
    result = await db.execute(
        select(ProgramDay)
        .where(ProgramDay.program_id == program_id)
        .order_by(ProgramDay.order_index)
    )
    return list(result.scalars().all())


async def create_program_day_exercise(
    db: AsyncSession, *, program_day_id: uuid.UUID, **kwargs
) -> ProgramDayExercise:
    exercise = ProgramDayExercise(program_day_id=program_day_id, **kwargs)
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def list_program_day_exercises(
    db: AsyncSession, program_day_id: uuid.UUID
) -> list[ProgramDayExercise]:
    result = await db.execute(
        select(ProgramDayExercise)
        .where(ProgramDayExercise.program_day_id == program_day_id)
        .order_by(ProgramDayExercise.order_index)
    )
    return list(result.scalars().all())
