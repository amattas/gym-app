import uuid
from datetime import datetime

import strawberry


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
    async def clients(self, gym_id: uuid.UUID) -> list[ClientType]:
        return []

    @strawberry.field
    async def client(self, client_id: uuid.UUID) -> ClientType | None:
        return None

    @strawberry.field
    async def trainers(self, gym_id: uuid.UUID) -> list[TrainerType]:
        return []

    @strawberry.field
    async def workouts(
        self, gym_id: uuid.UUID, client_id: uuid.UUID | None = None
    ) -> list[WorkoutType]:
        return []

    @strawberry.field
    async def schedules(
        self, gym_id: uuid.UUID, trainer_id: uuid.UUID | None = None
    ) -> list[ScheduleType]:
        return []

    @strawberry.field
    async def memberships(
        self, gym_id: uuid.UUID, client_id: uuid.UUID | None = None
    ) -> list[MembershipType]:
        return []

    @strawberry.field
    async def locations(self, gym_id: uuid.UUID) -> list[LocationType]:
        return []


schema = strawberry.Schema(query=Query)
