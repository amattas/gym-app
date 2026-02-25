import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.cache.cache_service import cache_delete
from gym_api.models.program import Program, TemplateScope
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


def _cache_key(program_id: uuid.UUID) -> str:
    return f"program:{program_id}"


async def create_program(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    created_by_trainer_id: uuid.UUID | None = None,
    **kwargs,
) -> Program:
    program = Program(gym_id=gym_id, created_by_trainer_id=created_by_trainer_id, **kwargs)
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return program


async def get_program(db: AsyncSession, gym_id: uuid.UUID, program_id: uuid.UUID) -> Program | None:
    result = await db.execute(
        select(Program).where(Program.program_id == program_id, Program.gym_id == gym_id)
    )
    return result.scalar_one_or_none()


async def list_programs(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    template_scope: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Program], dict]:
    query = select(Program).where(Program.gym_id == gym_id)
    if template_scope:
        query = query.where(Program.template_scope == TemplateScope(template_scope))
    query = apply_cursor_pagination(
        query, order_column=Program.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_program(db: AsyncSession, program: Program, **kwargs) -> Program:
    for key, value in kwargs.items():
        if value is not None:
            setattr(program, key, value)
    await db.commit()
    await db.refresh(program)
    await cache_delete(_cache_key(program.program_id))
    return program


async def delete_program(db: AsyncSession, program: Program) -> None:
    program_id = program.program_id
    await db.delete(program)
    await db.commit()
    await cache_delete(_cache_key(program_id))
