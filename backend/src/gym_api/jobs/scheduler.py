import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from gym_api.jobs.cleanup import cleanup_expired_tokens
from gym_api.jobs.membership_expiry import check_membership_expiry

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler() -> AsyncIOScheduler:
    # Nightly at 2 AM
    scheduler.add_job(
        check_membership_expiry,
        "cron",
        hour=2,
        minute=0,
        id="membership_expiry",
        replace_existing=True,
    )
    # Every 6 hours
    scheduler.add_job(
        cleanup_expired_tokens,
        "interval",
        hours=6,
        id="token_cleanup",
        replace_existing=True,
    )
    return scheduler
