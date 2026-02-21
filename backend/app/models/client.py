"""Client model and related enumerations."""

import enum
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ClientStatus(str, enum.Enum):
    """Enumeration of possible client statuses."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Client(Base, TimestampMixin):
    """Represents a gym client (member) profile."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ClientStatus.ACTIVE.value
    )

    # Relationships
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User", foreign_keys=[user_id]
    )
    checkins: Mapped[list["CheckIn"]] = relationship(  # noqa: F821
        "CheckIn", back_populates="client", foreign_keys="[CheckIn.client_id]"
    )
