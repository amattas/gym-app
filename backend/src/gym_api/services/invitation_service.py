import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.trainer_invitation import TrainerInvitation

INVITATION_EXPIRY_DAYS = 7


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_invitation(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    email: str,
    invited_by: uuid.UUID,
) -> tuple[TrainerInvitation, str]:
    raw_token = secrets.token_urlsafe(48)
    invitation = TrainerInvitation(
        gym_id=gym_id,
        email=email,
        token_hash=_hash_token(raw_token),
        invited_by_user_id=invited_by,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=INVITATION_EXPIRY_DAYS),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation, raw_token


async def validate_invitation(
    db: AsyncSession, token: str
) -> TrainerInvitation | None:
    token_hash = _hash_token(token)
    result = await db.execute(
        select(TrainerInvitation).where(
            TrainerInvitation.token_hash == token_hash
        )
    )
    invitation = result.scalar_one_or_none()
    if not invitation:
        return None
    if invitation.is_used:
        return None
    if invitation.expires_at < datetime.now(timezone.utc):
        return None
    return invitation


async def accept_invitation(
    db: AsyncSession, invitation: TrainerInvitation
) -> None:
    invitation.is_used = True
    await db.commit()
