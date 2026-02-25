import logging
from datetime import datetime, timezone

from sqlalchemy import delete

from gym_api.database import async_session
from gym_api.models.password_reset import PasswordResetToken
from gym_api.models.refresh_token import RefreshToken
from gym_api.models.trainer_invitation import TrainerInvitation

logger = logging.getLogger(__name__)


async def cleanup_expired_tokens() -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as db:
        # Clean expired refresh tokens
        result = await db.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < now)
        )
        refresh_count = result.rowcount

        # Clean expired password reset tokens
        result = await db.execute(
            delete(PasswordResetToken).where(
                PasswordResetToken.expires_at < now
            )
        )
        reset_count = result.rowcount

        # Clean expired invitations
        result = await db.execute(
            delete(TrainerInvitation).where(
                TrainerInvitation.expires_at < now,
                TrainerInvitation.is_used.is_(False),
            )
        )
        invite_count = result.rowcount

        await db.commit()

    logger.info(
        "Token cleanup: refresh=%d reset=%d invitations=%d",
        refresh_count,
        reset_count,
        invite_count,
    )
