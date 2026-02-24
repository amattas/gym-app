import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_api.database import Base
from gym_api.models.exercise import Exercise  # noqa: F401 — used by relationship forward ref


class Workout(Base):
    __tablename__ = "workouts"

    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False, index=True)
    trainer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    program_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.program_id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")

    exercises: Mapped[list["WorkoutExercise"]] = relationship(back_populates="workout", lazy="selectin")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workouts.workout_id"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.exercise_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="incomplete")
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(lazy="selectin")
    sets: Mapped[list["WorkoutSet"]] = relationship(back_populates="workout_exercise", lazy="selectin")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    workout_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_exercises.workout_exercise_id"), nullable=False)
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_amrap: Mapped[bool] = mapped_column(Boolean, default=False)

    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
    measurements: Mapped[list["WorkoutSetMeasurement"]] = relationship(back_populates="workout_set", lazy="selectin")


class WorkoutSetMeasurement(Base):
    __tablename__ = "workout_set_measurements"

    measurement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_sets.workout_set_id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    workout_set: Mapped["WorkoutSet"] = relationship(back_populates="measurements")
