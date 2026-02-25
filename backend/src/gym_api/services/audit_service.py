import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.audit_log import AuditLog
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def log_event(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        gym_id=gym_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_audit_logs(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    action: str | None = None,
    resource_type: str | None = None,
    start_date=None,
    end_date=None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[AuditLog], dict]:
    query = select(AuditLog).where(AuditLog.gym_id == gym_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    query = apply_cursor_pagination(
        query, order_column=AuditLog.created_at, cursor=cursor, limit=limit, ascending=False
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination
