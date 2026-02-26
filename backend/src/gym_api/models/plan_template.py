import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class PlanType(str, enum.Enum):
    membership = "membership"
    punch_card = "punch_card"
    session_pack = "session_pack"
    drop_in = "drop_in"


class PlanStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    draft = "draft"


class PlanTemplate(Base):
    __tablename__ = "plan_templates"

    plan_template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_type: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        Enum(PlanStatus), default=PlanStatus.draft, nullable=False
    )
    visit_entitlement: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    plan_duration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    payment_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    modules_enabled: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_addon: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_primary_plan_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    addon_discount_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
