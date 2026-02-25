import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import require_role
from gym_api.models.user import User, UserRole
from gym_api.services import audit_service

router = APIRouter(prefix="/v1/gyms/{gym_id}/audit-logs", tags=["audit-logs"])


class AuditLogResponse(BaseModel):
    audit_log_id: uuid.UUID
    gym_id: uuid.UUID
    user_id: uuid.UUID | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=dict)
async def list_audit_logs(
    gym_id: uuid.UUID,
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_role(UserRole.gym_admin, UserRole.platform_admin)),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await audit_service.list_audit_logs(
        db, gym_id, action=action, resource_type=resource_type,
        start_date=start_date, end_date=end_date, cursor=cursor, limit=limit,
    )
    return {
        "data": [AuditLogResponse.model_validate(log) for log in items],
        "pagination": pagination,
    }
