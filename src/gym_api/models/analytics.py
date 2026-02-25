import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class WorkoutAnalytics(Base):
    __tablename__ = "workout_analytics"

    analytics_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workouts.workout_id"), unique=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False, index=True)
    total_weight_lifted_lbs: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exercises_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    prs_achieved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    volume_by_muscle_group: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
