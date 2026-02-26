import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class OnboardingStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    restricted = "restricted"


class StripeAccount(Base):
    __tablename__ = "stripe_accounts"

    stripe_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True, nullable=False
    )
    stripe_connect_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    onboarding_status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus), default=OnboardingStatus.pending, nullable=False
    )
    charges_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payouts_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    processing_fee_percentage: Mapped[float | None] = mapped_column(nullable=True)
    pass_fees_to_client: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
