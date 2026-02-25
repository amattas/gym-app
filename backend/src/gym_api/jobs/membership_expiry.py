import logging

logger = logging.getLogger(__name__)


async def check_membership_expiry() -> None:
    # Placeholder for membership expiration check
    # In production: query memberships where end_date <= today,
    # update status, send notification emails
    logger.info("Running membership expiry check")
