import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class PRType(str, enum.Enum):
    one_rm = "1RM"
    three_rm = "3RM"
    five_rm = "5RM"
    ten_rm = "10RM"
    volume = "volume"


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    pr_type: Mapped[PRType] = mapped_column(Enum(PRType), index=True, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    volume_kg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    achieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
