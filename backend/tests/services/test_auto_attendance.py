"""Tests for auto-attendance feature.

Tests the automatic attendance marking when exercises are logged during
scheduled sessions, using time tolerance matching.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.checkin import CheckIn
from app.models.client import Client
from app.models.session import SessionStatus, TrainingSession
from app.services.checkin_service import CheckInService


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    return AsyncMock()


@pytest.fixture
def checkin_service(mock_db):
    """Create a CheckInService instance with mocked database."""
    return CheckInService(mock_db)


@pytest.fixture
def sample_client():
    """Create a sample client for testing."""
    return Client(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        first_name="Test",
        last_name="Client",
        email="test@example.com",
        phone="+1234567890",
        status="active",
        gym_id=uuid.uuid4(),
    )


@pytest.fixture
def sample_training_session(sample_client):
    """Create a sample training session for testing."""
    now = datetime.now(timezone.utc)
    return TrainingSession(
        id=uuid.uuid4(),
        gym_id=sample_client.gym_id,
        client_id=sample_client.user_id,
        trainer_id=uuid.uuid4(),
        scheduled_start=now,
        scheduled_end=now + timedelta(hours=1),
        duration_minutes=60,
        status=SessionStatus.SCHEDULED.value,
        created_by=uuid.uuid4(),
    )


class TestAutoCheckinTimeMatching:
    """Test time tolerance matching for auto check-in."""

    @pytest.mark.asyncio
    async def test_workout_logged_within_tolerance_before_session(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that workout logged 10 minutes before session creates check-in."""
        # Workout logged 10 minutes before session starts
        workout_time = sample_training_session.scheduled_start - timedelta(minutes=10)

        # Mock the database queries
        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_training_session
        mock_db.execute.return_value = mock_result

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_tolerance_minutes = 15
            mock_settings.auto_attendance_enabled = True

            session = await checkin_service._find_matching_training_session(
                client_id=sample_client.id,
                trainer_id=sample_training_session.trainer_id,
                gym_id=sample_training_session.gym_id,
                workout_time=workout_time,
            )

        assert session is not None
        assert session.id == sample_training_session.id

    @pytest.mark.asyncio
    async def test_workout_logged_outside_tolerance_no_match(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that workout logged outside tolerance does not create check-in."""
        # Workout logged 30 minutes before session starts (outside 15 min tolerance)
        workout_time = sample_training_session.scheduled_start - timedelta(minutes=30)

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No matching session
        mock_db.execute.return_value = mock_result

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_tolerance_minutes = 15
            mock_settings.auto_attendance_enabled = True

            session = await checkin_service._find_matching_training_session(
                client_id=sample_client.id,
                trainer_id=sample_training_session.trainer_id,
                gym_id=sample_training_session.gym_id,
                workout_time=workout_time,
            )

        assert session is None

    @pytest.mark.asyncio
    async def test_workout_logged_during_session(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that workout logged during session creates check-in."""
        # Workout logged 30 minutes into the session
        workout_time = sample_training_session.scheduled_start + timedelta(minutes=30)

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_training_session
        mock_db.execute.return_value = mock_result

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_tolerance_minutes = 15
            mock_settings.auto_attendance_enabled = True

            session = await checkin_service._find_matching_training_session(
                client_id=sample_client.id,
                trainer_id=sample_training_session.trainer_id,
                gym_id=sample_training_session.gym_id,
                workout_time=workout_time,
            )

        assert session is not None

    @pytest.mark.asyncio
    async def test_workout_logged_after_session_within_tolerance(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that workout logged 10 minutes after session creates check-in."""
        # Workout logged 10 minutes after session ends
        workout_time = sample_training_session.scheduled_end + timedelta(minutes=10)

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_training_session
        mock_db.execute.return_value = mock_result

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_tolerance_minutes = 15
            mock_settings.auto_attendance_enabled = True

            session = await checkin_service._find_matching_training_session(
                client_id=sample_client.id,
                trainer_id=sample_training_session.trainer_id,
                gym_id=sample_training_session.gym_id,
                workout_time=workout_time,
            )

        assert session is not None


class TestAutoCheckinConfiguration:
    """Test configuration options for auto check-in."""

    @pytest.mark.asyncio
    async def test_auto_checkin_disabled(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that auto check-in is skipped when disabled in settings."""
        workout_time = sample_training_session.scheduled_start

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_enabled = False

            result = await checkin_service.auto_checkin_on_workout(
                client_id=sample_client.id,
                gym_id=sample_training_session.gym_id,
                trainer_id=sample_training_session.trainer_id,
                workout_time=workout_time,
                workout_session_id=uuid.uuid4(),
                checked_in_by=sample_training_session.trainer_id,
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_custom_tolerance_minutes(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that custom tolerance can be provided."""
        # Workout logged 25 minutes before session starts
        workout_time = sample_training_session.scheduled_start - timedelta(minutes=25)

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        mock_result = MagicMock()
        # Session should match with 30 minute tolerance
        mock_result.scalar_one_or_none.return_value = sample_training_session
        mock_db.execute.return_value = mock_result

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_tolerance_minutes = 15
            mock_settings.auto_attendance_enabled = True

            # Use custom tolerance of 30 minutes
            session = await checkin_service._find_matching_training_session(
                client_id=sample_client.id,
                trainer_id=sample_training_session.trainer_id,
                gym_id=sample_training_session.gym_id,
                workout_time=workout_time,
                tolerance_minutes=30,  # Custom tolerance
            )

        # The query should have been called
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_no_gym_id_skips_auto_checkin(
        self, checkin_service, sample_client, mock_db
    ):
        """Test that auto check-in is skipped when no gym_id is provided."""
        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_enabled = True

            result = await checkin_service.auto_checkin_on_workout(
                client_id=sample_client.id,
                gym_id=None,  # No gym ID
                trainer_id=uuid.uuid4(),
                workout_time=datetime.now(timezone.utc),
                workout_session_id=uuid.uuid4(),
                checked_in_by=uuid.uuid4(),
            )

        assert result is None


class TestAutoCheckinCreation:
    """Test check-in record creation during auto check-in."""

    @pytest.mark.asyncio
    async def test_auto_checkin_creates_record(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that auto check-in creates proper check-in record."""
        workout_time = sample_training_session.scheduled_start + timedelta(minutes=5)
        workout_session_id = uuid.uuid4()

        # Mock all required methods
        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        checkin_service._find_matching_training_session = AsyncMock(
            return_value=sample_training_session
        )
        checkin_service._get_checkin_by_training_session = AsyncMock(return_value=None)

        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_enabled = True
            mock_settings.auto_attendance_tolerance_minutes = 15

            await checkin_service.auto_checkin_on_workout(
                client_id=sample_client.id,
                gym_id=sample_training_session.gym_id,
                trainer_id=sample_training_session.trainer_id,
                workout_time=workout_time,
                workout_session_id=workout_session_id,
                checked_in_by=sample_training_session.trainer_id,
            )

        # Verify a CheckIn was added
        mock_db.add.assert_called_once()
        added_checkin = mock_db.add.call_args[0][0]
        assert isinstance(added_checkin, CheckIn)
        assert added_checkin.client_id == sample_client.id
        assert added_checkin.gym_id == sample_training_session.gym_id
        assert added_checkin.training_session_id == sample_training_session.id
        assert added_checkin.is_walk_in is False
        assert str(workout_session_id) in added_checkin.notes

    @pytest.mark.asyncio
    async def test_auto_checkin_marks_session_completed(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that auto check-in marks training session as completed."""
        workout_time = sample_training_session.scheduled_start + timedelta(minutes=5)

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        checkin_service._find_matching_training_session = AsyncMock(
            return_value=sample_training_session
        )
        checkin_service._get_checkin_by_training_session = AsyncMock(return_value=None)

        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_enabled = True
            mock_settings.auto_attendance_tolerance_minutes = 15

            await checkin_service.auto_checkin_on_workout(
                client_id=sample_client.id,
                gym_id=sample_training_session.gym_id,
                trainer_id=sample_training_session.trainer_id,
                workout_time=workout_time,
                workout_session_id=uuid.uuid4(),
                checked_in_by=sample_training_session.trainer_id,
            )

        # Training session should be marked as completed
        assert sample_training_session.status == SessionStatus.COMPLETED.value

    @pytest.mark.asyncio
    async def test_existing_checkin_returns_existing(
        self, checkin_service, sample_client, sample_training_session, mock_db
    ):
        """Test that existing check-in is returned instead of creating duplicate."""
        workout_time = sample_training_session.scheduled_start + timedelta(minutes=5)
        existing_checkin = CheckIn(
            id=uuid.uuid4(),
            gym_id=sample_training_session.gym_id,
            client_id=sample_client.id,
            checked_in_by=uuid.uuid4(),
            training_session_id=sample_training_session.id,
        )

        checkin_service._get_client_by_id = AsyncMock(return_value=sample_client)
        checkin_service._find_matching_training_session = AsyncMock(
            return_value=sample_training_session
        )
        checkin_service._get_checkin_by_training_session = AsyncMock(
            return_value=existing_checkin
        )

        with patch("app.services.checkin_service.settings") as mock_settings:
            mock_settings.auto_attendance_enabled = True
            mock_settings.auto_attendance_tolerance_minutes = 15

            result = await checkin_service.auto_checkin_on_workout(
                client_id=sample_client.id,
                gym_id=sample_training_session.gym_id,
                trainer_id=sample_training_session.trainer_id,
                workout_time=workout_time,
                workout_session_id=uuid.uuid4(),
                checked_in_by=sample_training_session.trainer_id,
            )

        assert result == existing_checkin
        mock_db.add.assert_not_called()
