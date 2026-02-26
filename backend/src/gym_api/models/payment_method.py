import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    payment_method_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    stripe_payment_method_id: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    exp_month: Mapped[int | None] = mapped_column(nullable=True)
    exp_year: Mapped[int | None] = mapped_column(nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
