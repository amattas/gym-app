"""Check-in model for tracking client gym attendance."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CheckIn(Base, TimestampMixin):
    """Represents a single check-in event for a client at a gym."""

    __tablename__ = "checkins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False
    )
    checked_in_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    check_in_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    check_out_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_sessions.id"),
        nullable=True,
    )
    is_walk_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client", back_populates="checkins", foreign_keys=[client_id]
    )
    checked_in_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[checked_in_by]
    )
    training_session: Mapped["TrainingSession | None"] = relationship(  # noqa: F821
        "TrainingSession", back_populates="checkin", foreign_keys=[training_session_id]
    )

    @property
    def duration_minutes(self) -> int | None:
        """Calculate duration of the visit in minutes."""
        if self.check_out_time and self.check_in_time:
            delta = self.check_out_time - self.check_in_time
            return int(delta.total_seconds() / 60)
        return None
