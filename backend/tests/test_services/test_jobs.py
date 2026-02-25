from unittest.mock import AsyncMock, MagicMock, patch

from gym_api.jobs.scheduler import setup_scheduler


def test_setup_scheduler_registers_jobs():
    sched = setup_scheduler()
    job_ids = [j.id for j in sched.get_jobs()]
    assert "membership_expiry" in job_ids
    assert "token_cleanup" in job_ids
    sched.remove_all_jobs()


async def test_cleanup_expired_tokens():
    mock_result = MagicMock()
    mock_result.rowcount = 5

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)

    with patch("gym_api.jobs.cleanup.async_session", return_value=mock_db):
        from gym_api.jobs.cleanup import cleanup_expired_tokens

        await cleanup_expired_tokens()

    assert mock_db.execute.call_count == 3
    mock_db.commit.assert_called_once()


async def test_check_membership_expiry():
    from gym_api.jobs.membership_expiry import check_membership_expiry

    # Should run without error (placeholder implementation)
    await check_membership_expiry()
