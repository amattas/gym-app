import uuid
from datetime import datetime

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from gym_api.database import async_session
from gym_api.models.client import Client
from gym_api.models.client_membership import ClientMembership
from gym_api.models.location import Location
from gym_api.models.schedule import Schedule
from gym_api.models.trainer import Trainer
from gym_api.models.workout import Workout


def _require_gym_access(info: Info, gym_id: uuid.UUID) -> None:
    ctx_gym = info.context.get("gym_id")
    if ctx_gym and ctx_gym != gym_id:
        raise PermissionError("Access denied to this gym")


@strawberry.type
class ClientType:
    client_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    status: str | None = None


@strawberry.type
class TrainerType:
    trainer_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    specializations: str | None = None


@strawberry.type
class WorkoutType:
    workout_id: uuid.UUID
    client_id: uuid.UUID
    trainer_id: uuid.UUID | None = None
    status: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@strawberry.type
class ScheduleType:
    schedule_id: uuid.UUID
    client_id: uuid.UUID | None = None
    trainer_id: uuid.UUID | None = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: str


@strawberry.type
class MembershipType:
    client_membership_id: uuid.UUID
    client_id: uuid.UUID
    plan_type: str
    status: str
    started_at: datetime | None = None
    expires_at: datetime | None = None


@strawberry.type
class LocationType:
    location_id: uuid.UUID
    name: str
    address: str | None = None
    city: str | None = None
    is_active: bool


@strawberry.type
class Query:
    @strawberry.field
    async def clients(
        self, info: Info, gym_id: uuid.UUID
    ) -> list[ClientType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            result = await db.execute(
                select(Client).where(
                    Client.gym_id == gym_id,
                    Client.deleted_at.is_(None),
                )
            )
            return [
                ClientType(
                    client_id=c.client_id,
                    first_name=c.first_name,
                    last_name=c.last_name,
                    email=c.email,
                    phone=c.phone,
                    status=c.status.value if c.status else None,
                )
                for c in result.scalars().all()
            ]

    @strawberry.field
    async def client(
        self, info: Info, client_id: uuid.UUID
    ) -> ClientType | None:
        async with async_session() as db:
            result = await db.execute(
                select(Client).where(
                    Client.client_id == client_id
                )
            )
            c = result.scalar_one_or_none()
            if not c:
                return None
            return ClientType(
                client_id=c.client_id,
                first_name=c.first_name,
                last_name=c.last_name,
                email=c.email,
                phone=c.phone,
                status=c.status.value if c.status else None,
            )

    @strawberry.field
    async def trainers(
        self, info: Info, gym_id: uuid.UUID
    ) -> list[TrainerType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            result = await db.execute(
                select(Trainer).where(Trainer.gym_id == gym_id)
            )
            return [
                TrainerType(
                    trainer_id=t.trainer_id,
                    first_name=t.first_name,
                    last_name=t.last_name,
                    email=t.email,
                    specializations=None,
                )
                for t in result.scalars().all()
            ]

    @strawberry.field
    async def workouts(
        self,
        info: Info,
        gym_id: uuid.UUID,
        client_id: uuid.UUID | None = None,
    ) -> list[WorkoutType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            q = select(Workout).where(Workout.gym_id == gym_id)
            if client_id:
                q = q.where(Workout.client_id == client_id)
            result = await db.execute(q.limit(100))
            return [
                WorkoutType(
                    workout_id=w.workout_id,
                    client_id=w.client_id,
                    trainer_id=w.trainer_id,
                    status=(
                        w.status.value if w.status else None
                    ),
                    started_at=w.started_at,
                    completed_at=w.ended_at,
                )
                for w in result.scalars().all()
            ]

    @strawberry.field
    async def schedules(
        self,
        info: Info,
        gym_id: uuid.UUID,
        trainer_id: uuid.UUID | None = None,
    ) -> list[ScheduleType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            q = select(Schedule).where(Schedule.gym_id == gym_id)
            if trainer_id:
                q = q.where(Schedule.trainer_id == trainer_id)
            result = await db.execute(q.limit(100))
            return [
                ScheduleType(
                    schedule_id=s.schedule_id,
                    client_id=s.client_id,
                    trainer_id=s.trainer_id,
                    scheduled_start=s.scheduled_start,
                    scheduled_end=s.scheduled_end,
                    status=(
                        s.status.value if s.status else ""
                    ),
                )
                for s in result.scalars().all()
            ]

    @strawberry.field
    async def memberships(
        self,
        info: Info,
        gym_id: uuid.UUID,
        client_id: uuid.UUID | None = None,
    ) -> list[MembershipType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            q = select(ClientMembership).where(
                ClientMembership.gym_id == gym_id
            )
            if client_id:
                q = q.where(
                    ClientMembership.client_id == client_id
                )
            result = await db.execute(q.limit(100))
            return [
                MembershipType(
                    client_membership_id=m.client_membership_id,
                    client_id=m.client_id,
                    plan_type=(
                        m.plan_type.value
                        if m.plan_type
                        else ""
                    ),
                    status=(
                        m.status.value if m.status else ""
                    ),
                    started_at=m.started_at,
                    expires_at=m.expires_at,
                )
                for m in result.scalars().all()
            ]

    @strawberry.field
    async def locations(
        self, info: Info, gym_id: uuid.UUID
    ) -> list[LocationType]:
        _require_gym_access(info, gym_id)
        async with async_session() as db:
            result = await db.execute(
                select(Location).where(
                    Location.gym_id == gym_id,
                    Location.is_active.is_(True),
                )
            )
            return [
                LocationType(
                    location_id=loc.location_id,
                    name=loc.name,
                    address=loc.address,
                    city=loc.city,
                    is_active=loc.is_active,
                )
                for loc in result.scalars().all()
            ]


schema = strawberry.Schema(query=Query)
