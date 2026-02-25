import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client_invitation import ClientInvitation


async def create_invitation(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    email: str,
    invited_by_user_id: uuid.UUID,
    expires_in_days: int = 7,
) -> tuple[ClientInvitation, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    invitation = ClientInvitation(
        gym_id=gym_id,
        client_id=client_id,
        email=email,
        token_hash=token_hash,
        invited_by_user_id=invited_by_user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation, token


async def accept_invitation(db: AsyncSession, *, token: str) -> ClientInvitation:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(ClientInvitation).where(
            ClientInvitation.token_hash == token_hash,
            ClientInvitation.is_used.is_(False),
            ClientInvitation.expires_at > datetime.now(timezone.utc),
        )
    )
    invitation = result.scalar_one_or_none()
    if not invitation:
        raise ValueError("Invalid or expired invitation")
    invitation.is_used = True
    await db.commit()
    await db.refresh(invitation)
    return invitation
