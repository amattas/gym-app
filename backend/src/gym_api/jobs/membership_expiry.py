import logging
from datetime import datetime, timezone

from sqlalchemy import select

from gym_api.database import async_session
from gym_api.models.client import Client

logger = logging.getLogger(__name__)


async def check_membership_expiry() -> None:
    # TODO: Replace with proper Membership model query once #194 (multi-location)
    # and membership models are implemented. For now, this logs a summary of
    # client status counts as a health check for the scheduler.
    now = datetime.now(timezone.utc)
    async with async_session() as db:
        result = await db.execute(
            select(Client.status, Client.client_id).where(Client.deleted_at.is_(None))
        )
        rows = result.all()

        status_counts: dict[str, int] = {}
        for status, _ in rows:
            key = status.value if hasattr(status, "value") else str(status)
            status_counts[key] = status_counts.get(key, 0) + 1

    logger.info(
        "Membership expiry check completed at %s — client statuses: %s",
        now.isoformat(),
        status_counts,
    )
