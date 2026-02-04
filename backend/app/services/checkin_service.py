"""Check-in service for managing client attendance operations."""

import uuid
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import get_logger
from app.models.checkin import CheckIn
from app.models.client import Client, ClientStatus
from app.models.session import SessionStatus, TrainingSession
from app.models.user import User
from app.schemas.checkin import (
    CheckInCreate,
    CheckInListFilters,
    CheckOutUpdate,
    ClientSearchResult,
    TrainingSessionSummary,
)

logger = get_logger(__name__)


class CheckInNotFoundError(Exception):
    """Raised when a check-in record is not found."""

    def __init__(self, checkin_id: uuid.UUID):
        self.checkin_id = checkin_id
        self.message = f"Check-in with ID '{checkin_id}' not found"
        super().__init__(self.message)


class ClientNotFoundError(Exception):
    """Raised when a client is not found."""

    def __init__(self, client_id: uuid.UUID):
        self.client_id = client_id
        self.message = f"Client with ID '{client_id}' not found"
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, user_id: uuid.UUID):
        self.user_id = user_id
        self.message = f"User with ID '{user_id}' not found"
        super().__init__(self.message)


class TrainingSessionNotFoundError(Exception):
    """Raised when a training session is not found."""

    def __init__(self, session_id: uuid.UUID):
        self.session_id = session_id
        self.message = f"Training session with ID '{session_id}' not found"
        super().__init__(self.message)


class ClientAlreadyCheckedInError(Exception):
    """Raised when a client already has an active check-in."""

    def __init__(self, client_id: uuid.UUID, checkin_id: uuid.UUID):
        self.client_id = client_id
        self.checkin_id = checkin_id
        self.message = f"Client '{client_id}' already has an active check-in (ID: {checkin_id})"
        super().__init__(self.message)


class CheckInAlreadyCompletedError(Exception):
    """Raised when trying to check out an already completed check-in."""

    def __init__(self, checkin_id: uuid.UUID):
        self.checkin_id = checkin_id
        self.message = f"Check-in '{checkin_id}' has already been checked out"
        super().__init__(self.message)


class InvalidCheckOutTimeError(Exception):
    """Raised when check-out time is before check-in time."""

    def __init__(self, check_in_time: datetime, check_out_time: datetime):
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.message = f"Check-out time ({check_out_time}) cannot be before check-in time ({check_in_time})"
        super().__init__(self.message)


class CheckInService:
    """Service for handling client check-in operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_client_by_id(self, client_id: uuid.UUID) -> Client | None:
        """Retrieve a client by their ID."""
        stmt = select(Client).where(Client.id == client_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by their ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_training_session_by_id(
        self, session_id: uuid.UUID
    ) -> TrainingSession | None:
        """Retrieve a training session by its ID."""
        stmt = select(TrainingSession).where(TrainingSession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_active_checkin_for_client(
        self, client_id: uuid.UUID, gym_id: uuid.UUID
    ) -> CheckIn | None:
        """Get the active (not checked out) check-in for a client at a gym."""
        stmt = select(CheckIn).where(
            and_(
                CheckIn.client_id == client_id,
                CheckIn.gym_id == gym_id,
                CheckIn.check_out_time.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_checkin(
        self,
        checkin_data: CheckInCreate,
        checked_in_by: uuid.UUID,
    ) -> CheckIn:
        """
        Create a new check-in for a client.

        Args:
            checkin_data: Check-in creation data
            checked_in_by: ID of the staff member performing the check-in

        Returns:
            Created CheckIn object

        Raises:
            ClientNotFoundError: If the client does not exist
            UserNotFoundError: If the staff user does not exist
            TrainingSessionNotFoundError: If the linked session does not exist
            ClientAlreadyCheckedInError: If client already has an active check-in
        """
        # Validate client exists
        client = await self._get_client_by_id(checkin_data.client_id)
        if not client:
            raise ClientNotFoundError(checkin_data.client_id)

        # Validate staff user exists
        staff_user = await self._get_user_by_id(checked_in_by)
        if not staff_user:
            raise UserNotFoundError(checked_in_by)

        # Validate training session exists if provided
        if checkin_data.training_session_id:
            session = await self._get_training_session_by_id(
                checkin_data.training_session_id
            )
            if not session:
                raise TrainingSessionNotFoundError(checkin_data.training_session_id)

        # Check for existing active check-in
        existing_checkin = await self._get_active_checkin_for_client(
            checkin_data.client_id, checkin_data.gym_id
        )
        if existing_checkin:
            raise ClientAlreadyCheckedInError(
                checkin_data.client_id, existing_checkin.id
            )

        # Determine check-in time
        check_in_time = checkin_data.check_in_time or datetime.now(timezone.utc)

        # Determine if this is a walk-in
        is_walk_in = checkin_data.is_walk_in
        if checkin_data.training_session_id is not None:
            is_walk_in = False

        # Create check-in record
        checkin = CheckIn(
            gym_id=checkin_data.gym_id,
            location_id=checkin_data.location_id,
            client_id=checkin_data.client_id,
            checked_in_by=checked_in_by,
            check_in_time=check_in_time,
            training_session_id=checkin_data.training_session_id,
            is_walk_in=is_walk_in,
            notes=checkin_data.notes,
        )

        self.db.add(checkin)
        await self.db.flush()
        await self.db.refresh(checkin)

        logger.info(
            "Client checked in",
            checkin_id=str(checkin.id),
            client_id=str(checkin.client_id),
            gym_id=str(checkin.gym_id),
            is_walk_in=is_walk_in,
            checked_in_by=str(checked_in_by),
            check_in_time=check_in_time.isoformat(),
        )

        return checkin

    async def checkout(
        self,
        checkin_id: uuid.UUID,
        checkout_data: CheckOutUpdate,
    ) -> CheckIn:
        """
        Check out a client from an active check-in.

        Args:
            checkin_id: ID of the check-in to complete
            checkout_data: Check-out data including optional time and notes

        Returns:
            Updated CheckIn object

        Raises:
            CheckInNotFoundError: If the check-in does not exist
            CheckInAlreadyCompletedError: If already checked out
            InvalidCheckOutTimeError: If check-out time is before check-in time
        """
        checkin = await self.get_checkin_by_id(checkin_id)
        if not checkin:
            raise CheckInNotFoundError(checkin_id)

        if checkin.check_out_time is not None:
            raise CheckInAlreadyCompletedError(checkin_id)

        # Determine check-out time
        check_out_time = checkout_data.check_out_time or datetime.now(timezone.utc)

        # Validate check-out time is after check-in time
        if check_out_time < checkin.check_in_time:
            raise InvalidCheckOutTimeError(checkin.check_in_time, check_out_time)

        # Update check-in record
        checkin.check_out_time = check_out_time
        if checkout_data.notes is not None:
            checkin.notes = checkout_data.notes

        await self.db.flush()
        await self.db.refresh(checkin)

        logger.info(
            "Client checked out",
            checkin_id=str(checkin_id),
            client_id=str(checkin.client_id),
            check_out_time=check_out_time.isoformat(),
            duration_minutes=checkin.duration_minutes,
        )

        return checkin

    async def get_checkin_by_id(
        self,
        checkin_id: uuid.UUID,
        include_relationships: bool = False,
    ) -> CheckIn | None:
        """
        Retrieve a check-in by its ID.

        Args:
            checkin_id: The check-in ID to search for
            include_relationships: Whether to eagerly load relationships

        Returns:
            CheckIn object if found, None otherwise
        """
        stmt = select(CheckIn).where(CheckIn.id == checkin_id)

        if include_relationships:
            stmt = stmt.options(
                selectinload(CheckIn.client),
                selectinload(CheckIn.checked_in_by_user),
                selectinload(CheckIn.training_session),
            )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_checkins(
        self,
        filters: CheckInListFilters,
        page: int = 1,
        page_size: int = 20,
        include_relationships: bool = False,
    ) -> tuple[list[CheckIn], int]:
        """
        Retrieve a paginated list of check-ins with optional filters.

        Args:
            filters: Filter parameters
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_relationships: Whether to eagerly load relationships

        Returns:
            Tuple of (list of check-ins, total count)
        """
        conditions = []

        if filters.gym_id:
            conditions.append(CheckIn.gym_id == filters.gym_id)
        if filters.location_id:
            conditions.append(CheckIn.location_id == filters.location_id)
        if filters.client_id:
            conditions.append(CheckIn.client_id == filters.client_id)
        if filters.checked_in_by:
            conditions.append(CheckIn.checked_in_by == filters.checked_in_by)
        if filters.is_walk_in is not None:
            conditions.append(CheckIn.is_walk_in == filters.is_walk_in)
        if filters.is_active is not None:
            if filters.is_active:
                conditions.append(CheckIn.check_out_time.is_(None))
            else:
                conditions.append(CheckIn.check_out_time.isnot(None))
        if filters.start_date:
            conditions.append(CheckIn.check_in_time >= filters.start_date)
        if filters.end_date:
            conditions.append(CheckIn.check_in_time <= filters.end_date)

        # Count query
        count_stmt = select(func.count(CheckIn.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Data query
        stmt = select(CheckIn)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        if include_relationships:
            stmt = stmt.options(
                selectinload(CheckIn.client),
                selectinload(CheckIn.checked_in_by_user),
                selectinload(CheckIn.training_session),
            )

        stmt = stmt.order_by(CheckIn.check_in_time.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(stmt)
        checkins = list(result.scalars().all())

        return checkins, total_count

    async def get_todays_checkins(
        self,
        gym_id: uuid.UUID,
        include_relationships: bool = False,
    ) -> list[CheckIn]:
        """
        Get all check-ins for today at a specific gym.

        Args:
            gym_id: Gym identifier
            include_relationships: Whether to eagerly load relationships

        Returns:
            List of check-ins for today
        """
        # Get start of today in UTC
        now = datetime.now(timezone.utc)
        start_of_day = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        filters = CheckInListFilters(
            gym_id=gym_id,
            start_date=start_of_day,
            end_date=end_of_day,
        )

        checkins, _ = await self.get_checkins(
            filters=filters,
            page=1,
            page_size=1000,  # Get all today's check-ins
            include_relationships=include_relationships,
        )

        return checkins

    async def get_active_checkins(
        self,
        gym_id: uuid.UUID,
        include_relationships: bool = False,
    ) -> list[CheckIn]:
        """
        Get all currently active (not checked out) check-ins at a gym.

        Args:
            gym_id: Gym identifier
            include_relationships: Whether to eagerly load relationships

        Returns:
            List of active check-ins
        """
        filters = CheckInListFilters(
            gym_id=gym_id,
            is_active=True,
        )

        checkins, _ = await self.get_checkins(
            filters=filters,
            page=1,
            page_size=1000,  # Get all active check-ins
            include_relationships=include_relationships,
        )

        return checkins

    async def search_clients_for_checkin(
        self,
        gym_id: uuid.UUID,
        search_query: str,
        limit: int = 20,
    ) -> list[ClientSearchResult]:
        """
        Search for clients by name or email for check-in purposes.

        Args:
            gym_id: Gym identifier
            search_query: Search term for name or email
            limit: Maximum number of results

        Returns:
            List of matching clients with check-in status
        """
        # Build search condition
        search_term = f"%{search_query.lower()}%"
        search_condition = or_(
            func.lower(Client.first_name).like(search_term),
            func.lower(Client.last_name).like(search_term),
            func.lower(Client.email).like(search_term),
            func.lower(
                func.concat(Client.first_name, " ", Client.last_name)
            ).like(search_term),
        )

        # Query clients
        stmt = (
            select(Client)
            .where(
                and_(
                    Client.gym_id == gym_id,
                    Client.status == ClientStatus.ACTIVE.value,
                    search_condition,
                )
            )
            .order_by(Client.last_name, Client.first_name)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        clients = list(result.scalars().all())

        # Get active check-ins and scheduled sessions for these clients
        client_ids = [c.id for c in clients]

        # Get active check-ins
        active_checkins_stmt = select(CheckIn).where(
            and_(
                CheckIn.client_id.in_(client_ids),
                CheckIn.gym_id == gym_id,
                CheckIn.check_out_time.is_(None),
            )
        )
        active_checkins_result = await self.db.execute(active_checkins_stmt)
        active_checkins = {c.client_id: c for c in active_checkins_result.scalars().all()}

        # Get today's scheduled sessions
        now = datetime.now(timezone.utc)
        start_of_day = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        sessions_stmt = select(TrainingSession).where(
            and_(
                TrainingSession.client_id.in_(client_ids),
                TrainingSession.gym_id == gym_id,
                TrainingSession.scheduled_start >= start_of_day,
                TrainingSession.scheduled_start < end_of_day,
                TrainingSession.status == SessionStatus.SCHEDULED.value,
            )
        )
        sessions_result = await self.db.execute(sessions_stmt)
        scheduled_sessions = {
            s.client_id: s for s in sessions_result.scalars().all()
        }

        # Build results
        results = []
        for client in clients:
            session = scheduled_sessions.get(client.id)
            session_summary = None
            if session:
                session_summary = TrainingSessionSummary(
                    id=session.id,
                    scheduled_start=session.scheduled_start,
                    scheduled_end=session.scheduled_end,
                    status=session.status,
                )

            results.append(
                ClientSearchResult(
                    id=client.id,
                    first_name=client.first_name,
                    last_name=client.last_name,
                    email=client.email,
                    phone=client.phone,
                    status=client.status,
                    has_active_checkin=client.id in active_checkins,
                    scheduled_session=session_summary,
                )
            )

        return results

    async def delete_checkin(self, checkin_id: uuid.UUID) -> bool:
        """
        Delete a check-in record.

        Args:
            checkin_id: ID of the check-in to delete

        Returns:
            True if deleted

        Raises:
            CheckInNotFoundError: If check-in does not exist
        """
        checkin = await self.get_checkin_by_id(checkin_id)
        if not checkin:
            raise CheckInNotFoundError(checkin_id)

        await self.db.delete(checkin)
        await self.db.flush()

        logger.info(
            "Check-in deleted",
            checkin_id=str(checkin_id),
        )

        return True

    async def _get_checkin_by_training_session(
        self,
        training_session_id: uuid.UUID,
    ) -> CheckIn | None:
        """Get an existing check-in for a training session."""
        stmt = select(CheckIn).where(
            CheckIn.training_session_id == training_session_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def auto_checkin_on_workout(
        self,
        client_id: uuid.UUID,
        gym_id: uuid.UUID | None,
        trainer_id: uuid.UUID | None,
        workout_time: datetime,
        workout_session_id: uuid.UUID,
        checked_in_by: uuid.UUID,
        tolerance_minutes: int | None = None,
    ) -> CheckIn | None:
        """
        Automatically create a check-in when exercises are logged.

        Called when the first workout set is created. Finds a matching
        training session within the configured time tolerance and creates
        a check-in record.

        The time tolerance is configurable via settings and defaults to 15 minutes.
        A workout is matched to a session if logged within:
        - tolerance minutes before session start
        - during the session
        - tolerance minutes after session end

        Args:
            client_id: The client's ID (from clients table)
            gym_id: The gym ID
            trainer_id: The trainer's user ID (optional)
            workout_time: When the workout started
            workout_session_id: The workout session ID
            checked_in_by: User performing the action
            tolerance_minutes: Override for time tolerance (defaults to settings)

        Returns:
            Created CheckIn if a matching session was found, None otherwise
        """
        # Check if auto-attendance is enabled
        if not settings.auto_attendance_enabled:
            logger.debug(
                "Auto-attendance is disabled, skipping auto check-in",
                client_id=str(client_id),
            )
            return None

        if not gym_id:
            logger.debug(
                "No gym_id provided, skipping auto check-in",
                client_id=str(client_id),
            )
            return None

        # Find matching training session for this client within time tolerance
        training_session = await self._find_matching_training_session(
            client_id=client_id,
            trainer_id=trainer_id,
            gym_id=gym_id,
            workout_time=workout_time,
            tolerance_minutes=tolerance_minutes,
        )

        if not training_session:
            logger.debug(
                "No matching training session found for auto check-in",
                client_id=str(client_id),
                workout_time=workout_time.isoformat(),
                tolerance_minutes=tolerance_minutes or settings.auto_attendance_tolerance_minutes,
            )
            return None

        # Check if check-in already exists for this training session
        existing_checkin = await self._get_checkin_by_training_session(
            training_session.id
        )
        if existing_checkin:
            logger.debug(
                "Check-in already exists for training session",
                training_session_id=str(training_session.id),
                checkin_id=str(existing_checkin.id),
            )
            return existing_checkin

        # Create the check-in
        checkin = CheckIn(
            gym_id=training_session.gym_id,
            location_id=training_session.location_id,
            client_id=client_id,
            checked_in_by=checked_in_by,
            check_in_time=datetime.now(timezone.utc),
            training_session_id=training_session.id,
            is_walk_in=False,
            notes=f"Auto check-in from workout session {workout_session_id}",
        )

        self.db.add(checkin)

        # Update training session status to completed
        training_session.status = SessionStatus.COMPLETED.value
        await self.db.flush()
        await self.db.refresh(checkin)

        logger.info(
            "Auto check-in created for workout",
            checkin_id=str(checkin.id),
            training_session_id=str(training_session.id),
            workout_session_id=str(workout_session_id),
            client_id=str(client_id),
            tolerance_minutes=tolerance_minutes or settings.auto_attendance_tolerance_minutes,
        )

        return checkin

    async def _find_matching_training_session(
        self,
        client_id: uuid.UUID,
        trainer_id: uuid.UUID | None,
        gym_id: uuid.UUID,
        workout_time: datetime,
        tolerance_minutes: int | None = None,
    ) -> TrainingSession | None:
        """
        Find a scheduled training session matching the workout context.

        Uses configurable time tolerance to match workouts logged within
        a time window around the scheduled session time.

        Args:
            client_id: The client's ID (from clients table)
            trainer_id: The trainer's user ID (optional)
            gym_id: The gym ID
            workout_time: When the workout started
            tolerance_minutes: Time tolerance in minutes (defaults to settings value)

        Returns:
            Matching TrainingSession if found, None otherwise
        """
        # Get the client to find their user_id
        client = await self._get_client_by_id(client_id)
        if not client:
            return None

        # TrainingSession.client_id refers to users.id, not clients.id
        # We need to use the client's user_id if available
        search_client_id = client.user_id if client.user_id else client_id

        # Use configured tolerance or default from settings
        if tolerance_minutes is None:
            tolerance_minutes = settings.auto_attendance_tolerance_minutes

        # Calculate time window for matching with tolerance
        # A workout matches a session if it falls within:
        # - tolerance minutes BEFORE session start, OR
        # - during the session, OR
        # - tolerance minutes AFTER session end
        tolerance_delta = timedelta(minutes=tolerance_minutes)

        # We look for sessions where:
        # workout_time >= scheduled_start - tolerance AND
        # workout_time <= scheduled_end + tolerance
        window_start = workout_time - tolerance_delta
        window_end = workout_time + tolerance_delta

        # Base conditions
        # Find sessions that overlap with our workout time +/- tolerance
        conditions = [
            TrainingSession.client_id == search_client_id,
            TrainingSession.status == SessionStatus.SCHEDULED.value,
            TrainingSession.gym_id == gym_id,
            # Session starts before or at (workout_time + tolerance)
            TrainingSession.scheduled_start <= window_end,
            # Session ends after or at (workout_time - tolerance)
            TrainingSession.scheduled_end >= window_start,
        ]

        # Add trainer filter if provided
        if trainer_id:
            conditions.append(TrainingSession.trainer_id == trainer_id)

        # Order by how close the session start is to the workout time
        stmt = (
            select(TrainingSession)
            .where(and_(*conditions))
            .order_by(
                # Prefer sessions closest to the workout time
                func.abs(
                    func.extract("epoch", TrainingSession.scheduled_start)
                    - func.extract("epoch", workout_time)
                )
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            logger.debug(
                "Found matching training session for auto check-in",
                training_session_id=str(session.id),
                client_id=str(client_id),
                workout_time=workout_time.isoformat(),
                session_start=session.scheduled_start.isoformat(),
                session_end=session.scheduled_end.isoformat(),
                tolerance_minutes=tolerance_minutes,
            )

        return session

    async def override_attendance(
        self,
        checkin_id: uuid.UUID,
        override_by: uuid.UUID,
        attended: bool,
        notes: str | None = None,
    ) -> CheckIn:
        """
        Override an existing check-in's attendance status.

        This allows staff to manually adjust attendance records.

        Args:
            checkin_id: The check-in to override
            override_by: The user ID performing the override
            attended: Whether the client attended (True) or should be marked no-show (False)
            notes: Optional notes explaining the override

        Returns:
            Updated CheckIn

        Raises:
            CheckInNotFoundError: If check-in not found
        """
        checkin = await self.get_checkin_by_id(checkin_id)
        if not checkin:
            raise CheckInNotFoundError(checkin_id)

        # Update the training session status if linked
        if checkin.training_session_id:
            training_session = await self._get_training_session_by_id(
                checkin.training_session_id
            )
            if training_session:
                new_status = (
                    SessionStatus.COMPLETED.value
                    if attended
                    else SessionStatus.NO_SHOW.value
                )
                training_session.status = new_status

        # Update check-in notes with override information
        override_note = f"Override by {override_by}: {'attended' if attended else 'no-show'}"
        if notes:
            override_note = f"{override_note} - {notes}"

        if checkin.notes:
            checkin.notes = f"{checkin.notes}\n{override_note}"
        else:
            checkin.notes = override_note

        await self.db.flush()
        await self.db.refresh(checkin)

        logger.info(
            "Attendance override applied",
            checkin_id=str(checkin_id),
            override_by=str(override_by),
            attended=attended,
            training_session_id=(
                str(checkin.training_session_id) if checkin.training_session_id else None
            ),
        )

        return checkin

    async def mark_session_no_show(
        self,
        training_session_id: uuid.UUID,
        marked_by: uuid.UUID,
        notes: str | None = None,
    ) -> TrainingSession:
        """
        Mark a training session as no-show.

        Used when a scheduled session has no workout logged.

        Args:
            training_session_id: The training session UUID
            marked_by: The user ID marking the no-show
            notes: Optional notes

        Returns:
            Updated TrainingSession

        Raises:
            TrainingSessionNotFoundError: If training session not found
        """
        training_session = await self._get_training_session_by_id(training_session_id)
        if not training_session:
            raise TrainingSessionNotFoundError(training_session_id)

        training_session.status = SessionStatus.NO_SHOW.value
        if notes:
            existing_notes = training_session.notes or ""
            training_session.notes = (
                f"{existing_notes}\nNo-show marked by {marked_by}: {notes}".strip()
            )

        await self.db.flush()
        await self.db.refresh(training_session)

        logger.info(
            "Training session marked as no-show",
            training_session_id=str(training_session_id),
            marked_by=str(marked_by),
        )

        return training_session

    async def detect_no_shows(
        self,
        gym_id: uuid.UUID | None = None,
        cutoff_time: datetime | None = None,
    ) -> list[TrainingSession]:
        """
        Detect and mark no-shows for sessions past their end time.

        Finds scheduled sessions that have ended with no associated workout
        or check-in and marks them as no-show.

        Args:
            gym_id: Optional gym ID to filter by
            cutoff_time: Time after which sessions are considered missed.
                        Defaults to current time.

        Returns:
            List of sessions marked as no-show
        """
        from app.models.workout import WorkoutSession

        if cutoff_time is None:
            cutoff_time = datetime.now(timezone.utc)

        # Find scheduled sessions past their end time
        conditions = [
            TrainingSession.status == SessionStatus.SCHEDULED.value,
            TrainingSession.scheduled_end < cutoff_time,
        ]

        if gym_id:
            conditions.append(TrainingSession.gym_id == gym_id)

        stmt = select(TrainingSession).where(and_(*conditions))
        result = await self.db.execute(stmt)
        sessions = list(result.scalars().all())

        no_show_sessions = []

        for session in sessions:
            # Check if there's a check-in for this session
            existing_checkin = await self._get_checkin_by_training_session(session.id)
            if existing_checkin:
                continue  # Has check-in, not a no-show

            # Check if there's a workout session linked to this training session
            workout_stmt = select(WorkoutSession).where(
                WorkoutSession.scheduled_session_id == session.id
            )
            workout_result = await self.db.execute(workout_stmt)
            workout_session = workout_result.scalar_one_or_none()

            if workout_session:
                continue  # Has workout, not a no-show

            # Mark as no-show
            session.status = SessionStatus.NO_SHOW.value
            session.notes = (
                f"{session.notes or ''}\n"
                f"Auto-detected no-show at {cutoff_time.isoformat()}"
            ).strip()
            no_show_sessions.append(session)

        if no_show_sessions:
            await self.db.flush()

            logger.info(
                "No-show detection completed",
                gym_id=str(gym_id) if gym_id else "all",
                sessions_marked=len(no_show_sessions),
                session_ids=[str(s.id) for s in no_show_sessions],
            )

        return no_show_sessions

    async def get_client_attendance_history(
        self,
        client_id: uuid.UUID,
        gym_id: uuid.UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CheckIn]:
        """
        Get attendance history for a client.

        Args:
            client_id: The client's UUID
            gym_id: Optional gym filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum results
            offset: Results offset

        Returns:
            List of CheckIn records
        """
        conditions = [CheckIn.client_id == client_id]

        if gym_id:
            conditions.append(CheckIn.gym_id == gym_id)
        if start_date:
            conditions.append(CheckIn.check_in_time >= start_date)
        if end_date:
            conditions.append(CheckIn.check_in_time <= end_date)

        stmt = (
            select(CheckIn)
            .where(and_(*conditions))
            .order_by(CheckIn.check_in_time.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())


def get_checkin_service(db: AsyncSession) -> CheckInService:
    """Factory function to create CheckInService instance."""
    return CheckInService(db)
