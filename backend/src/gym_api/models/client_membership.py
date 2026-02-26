import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class MembershipStatus(str, enum.Enum):
    active = "active"
    trial = "trial"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"
    pending = "pending"


class ClientMembership(Base):
    __tablename__ = "client_memberships"

    client_membership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    plan_template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus), default=MembershipStatus.active, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    visit_entitlement: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    visits_used_this_period: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_visits_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pause_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cancellation_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    base_membership_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
