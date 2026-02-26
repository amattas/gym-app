import logging
from datetime import datetime, timezone

from gym_api.database import async_session
from gym_api.services import membership_service

logger = logging.getLogger(__name__)


async def check_membership_expiry() -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as db:
        trial_count = await membership_service.process_trial_conversions(db)
        expired_count = await membership_service.process_expired_memberships(db)
        cancelled_count = await membership_service.process_pending_cancellations(db)
        reset_count = await membership_service.process_period_resets(db)

    logger.info(
        "Membership check at %s — trials_converted: %d, expired: %d, cancelled: %d, resets: %d",
        now.isoformat(),
        trial_count,
        expired_count,
        cancelled_count,
        reset_count,
    )
