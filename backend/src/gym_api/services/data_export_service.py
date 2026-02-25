import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.data_request import DataExportRequest


async def create_export_request(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    format: str = "json",
) -> DataExportRequest:
    request = DataExportRequest(
        gym_id=gym_id,
        client_id=client_id,
        format=format,
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def get_export_request(
    db: AsyncSession, export_id: uuid.UUID
) -> DataExportRequest | None:
    result = await db.execute(
        select(DataExportRequest).where(DataExportRequest.export_id == export_id)
    )
    return result.scalar_one_or_none()
