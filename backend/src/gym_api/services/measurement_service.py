import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client import Client
from gym_api.models.measurement import Measurement, MeasurementType
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


def _calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)


async def create_measurement(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    type: str,
    value: float,
    unit: str,
) -> Measurement:
    bmi = None
    if type == MeasurementType.weight.value:
        # Auto-calculate BMI if client has height
        result = await db.execute(
            select(Client).where(Client.client_id == client_id, Client.gym_id == gym_id)
        )
        client = result.scalar_one_or_none()
        if client and client.height_cm:
            bmi = _calculate_bmi(value, float(client.height_cm))

    measurement = Measurement(
        gym_id=gym_id,
        client_id=client_id,
        type=MeasurementType(type),
        value=value,
        unit=unit,
        bmi=bmi,
    )
    db.add(measurement)
    await db.commit()
    await db.refresh(measurement)
    return measurement


async def get_measurement(
    db: AsyncSession, gym_id: uuid.UUID, measurement_id: uuid.UUID
) -> Measurement | None:
    result = await db.execute(
        select(Measurement).where(
            Measurement.measurement_id == measurement_id, Measurement.gym_id == gym_id
        )
    )
    return result.scalar_one_or_none()


async def list_measurements(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    client_id: uuid.UUID | None = None,
    type: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[Measurement], dict]:
    query = select(Measurement).where(Measurement.gym_id == gym_id)
    if client_id:
        query = query.where(Measurement.client_id == client_id)
    if type:
        query = query.where(Measurement.type == MeasurementType(type))
    query = apply_cursor_pagination(
        query, order_column=Measurement.measured_at, cursor=cursor, limit=limit, ascending=False
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "measured_at")
    return items, pagination
