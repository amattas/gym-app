import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.note import Note
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_note(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    notable_type: str,
    notable_id: uuid.UUID,
    author_user_id: uuid.UUID,
    content: str,
) -> Note:
    note = Note(
        gym_id=gym_id,
        notable_type=notable_type,
        notable_id=notable_id,
        author_user_id=author_user_id,
        content=content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def list_notes(
    db: AsyncSession,
    gym_id: uuid.UUID,
    notable_type: str,
    notable_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Note], dict]:
    query = select(Note).where(
        Note.gym_id == gym_id,
        Note.notable_type == notable_type,
        Note.notable_id == notable_id,
    )
    query = apply_cursor_pagination(
        query, order_column=Note.created_at, cursor=cursor, limit=limit, ascending=False
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_note(
    db: AsyncSession, *, note_id: uuid.UUID, content: str
) -> Note | None:
    result = await db.execute(
        select(Note).where(Note.note_id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        return None
    note.content = content
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, *, note_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Note).where(Note.note_id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        return False
    await db.delete(note)
    await db.commit()
    return True
