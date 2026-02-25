import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class MeasurementType(str, enum.Enum):
    weight = "weight"
    body_fat = "body_fat"
    chest = "chest"
    waist = "waist"
    hips = "hips"
    bicep = "bicep"
    thigh = "thigh"
    calf = "calf"


class Measurement(Base):
    __tablename__ = "measurements"

    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    type: Mapped[MeasurementType] = mapped_column(Enum(MeasurementType), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    bmi: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
