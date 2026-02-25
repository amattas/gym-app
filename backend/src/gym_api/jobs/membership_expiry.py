import logging
from datetime import datetime, timezone

from gym_api.database import async_session
from gym_api.services import membership_service

logger = logging.getLogger(__name__)


async def check_membership_expiry() -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as db:
        expired_count = await membership_service.process_expired_memberships(db)
        cancelled_count = await membership_service.process_pending_cancellations(db)
        reset_count = await membership_service.process_period_resets(db)

    logger.info(
        "Membership expiry check completed at %s — expired: %d, cancelled: %d, period_resets: %d",
        now.isoformat(),
        expired_count,
        cancelled_count,
        reset_count,
    )
