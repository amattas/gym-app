import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class DomainType(str, enum.Enum):
    email = "email"
    login = "login"


class DomainStatus(str, enum.Enum):
    pending = "pending"
    verifying = "verifying"
    active = "active"
    failed = "failed"


class CustomDomain(Base):
    __tablename__ = "custom_domains"

    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    domain_type: Mapped[DomainType] = mapped_column(Enum(DomainType), nullable=False)
    status: Mapped[DomainStatus] = mapped_column(
        Enum(DomainStatus), default=DomainStatus.pending, nullable=False
    )
    dns_records: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
