import enum
import uuid
from datetime import datetime, time

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class ScheduleStatus(str, enum.Enum):
    tentative = "tentative"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "canceled"
    no_show = "no_show"


class ExceptionType(str, enum.Enum):
    unavailable = "unavailable"
    modified_hours = "modified_hours"


class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    trainer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    location_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus), default=ScheduleStatus.tentative, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    trainer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    day_of_week: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)


class TrainerException(Base):
    __tablename__ = "trainer_exceptions"

    trainer_exception_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trainer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    exception_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    exception_type: Mapped[ExceptionType] = mapped_column(
        Enum(ExceptionType), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
