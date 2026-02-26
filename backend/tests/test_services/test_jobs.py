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
    mock_db = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("gym_api.jobs.membership_expiry.async_session", return_value=mock_db),
        patch(
            "gym_api.jobs.membership_expiry.membership_service.process_trial_conversions",
            new_callable=AsyncMock,
            return_value=0,
        ) as trial_mock,
        patch(
            "gym_api.jobs.membership_expiry.membership_service.process_expired_memberships",
            new_callable=AsyncMock,
            return_value=2,
        ) as expired_mock,
        patch(
            "gym_api.jobs.membership_expiry.membership_service.process_pending_cancellations",
            new_callable=AsyncMock,
            return_value=1,
        ) as cancel_mock,
        patch(
            "gym_api.jobs.membership_expiry.membership_service.process_period_resets",
            new_callable=AsyncMock,
            return_value=3,
        ) as reset_mock,
    ):
        from gym_api.jobs.membership_expiry import check_membership_expiry

        await check_membership_expiry()

    trial_mock.assert_called_once_with(mock_db)
    expired_mock.assert_called_once_with(mock_db)
    cancel_mock.assert_called_once_with(mock_db)
    reset_mock.assert_called_once_with(mock_db)
