import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.client_membership import ClientMembership, MembershipStatus
from gym_api.models.plan_template import PlanTemplate
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_membership(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    plan_template_id: uuid.UUID,
    started_at: datetime | None = None,
    base_membership_id: uuid.UUID | None = None,
) -> ClientMembership:
    template = await db.execute(
        select(PlanTemplate).where(
            PlanTemplate.plan_template_id == plan_template_id,
            PlanTemplate.gym_id == gym_id,
        )
    )
    template = template.scalar_one_or_none()
    if not template:
        raise ValueError("Plan template not found")

    now = datetime.now(timezone.utc)
    start = started_at or now

    visit_entitlement = template.visit_entitlement
    expires_at = None
    period_end = None

    if template.plan_duration:
        duration_months = template.plan_duration.get("months", 0)
        duration_days = template.plan_duration.get("days", 0)
        if duration_months:
            month = start.month + duration_months
            year = start.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            day = min(start.day, 28)
            expires_at = start.replace(year=year, month=month, day=day)
        elif duration_days:
            expires_at = start + timedelta(days=duration_days)

    total_visits = None
    if visit_entitlement:
        total_visits = visit_entitlement.get("total_visits")

    period_start = start
    if template.plan_duration and template.plan_duration.get("period_days"):
        period_end = start + timedelta(days=template.plan_duration["period_days"])
    elif expires_at:
        period_end = expires_at

    membership = ClientMembership(
        gym_id=gym_id,
        client_id=client_id,
        plan_template_id=plan_template_id,
        plan_type=template.plan_type.value,
        status=MembershipStatus.active,
        started_at=start,
        expires_at=expires_at,
        visit_entitlement=visit_entitlement,
        visits_used_this_period=0,
        total_visits_remaining=total_visits,
        current_period_start=period_start,
        current_period_end=period_end,
        base_membership_id=base_membership_id,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def get_membership(
    db: AsyncSession, gym_id: uuid.UUID, membership_id: uuid.UUID
) -> ClientMembership | None:
    result = await db.execute(
        select(ClientMembership).where(
            ClientMembership.client_membership_id == membership_id,
            ClientMembership.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_client_memberships(
    db: AsyncSession,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    *,
    status: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[ClientMembership], dict]:
    query = select(ClientMembership).where(
        ClientMembership.gym_id == gym_id,
        ClientMembership.client_id == client_id,
    )
    if status:
        query = query.where(ClientMembership.status == status)
    query = apply_cursor_pagination(
        query, order_column=ClientMembership.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def pause_membership(
    db: AsyncSession, membership: ClientMembership, *, reason: str | None = None
) -> ClientMembership:
    if membership.status != MembershipStatus.active:
        raise ValueError("Only active memberships can be paused")
    now = datetime.now(timezone.utc)
    membership.status = MembershipStatus.paused
    membership.pause_info = {
        "paused_at": now.isoformat(),
        "reason": reason,
    }
    await db.commit()
    await db.refresh(membership)
    return membership


async def unpause_membership(
    db: AsyncSession, membership: ClientMembership
) -> ClientMembership:
    if membership.status != MembershipStatus.paused:
        raise ValueError("Only paused memberships can be unpaused")
    now = datetime.now(timezone.utc)
    pause_info = membership.pause_info or {}
    paused_at_str = pause_info.get("paused_at")
    if paused_at_str and membership.expires_at:
        paused_at = datetime.fromisoformat(paused_at_str)
        paused_days = (now - paused_at).days
        membership.expires_at = membership.expires_at + timedelta(days=paused_days)
        if membership.current_period_end:
            membership.current_period_end = membership.current_period_end + timedelta(
                days=paused_days
            )
    membership.status = MembershipStatus.active
    membership.pause_info = None
    await db.commit()
    await db.refresh(membership)
    return membership


async def cancel_membership(
    db: AsyncSession,
    membership: ClientMembership,
    *,
    reason: str | None = None,
    cancel_immediately: bool = False,
) -> ClientMembership:
    if membership.status in (MembershipStatus.cancelled, MembershipStatus.expired):
        raise ValueError("Membership is already cancelled or expired")

    now = datetime.now(timezone.utc)

    if cancel_immediately or not membership.current_period_end:
        membership.status = MembershipStatus.cancelled
        membership.cancellation_info = {
            "cancelled_at": now.isoformat(),
            "reason": reason,
            "effective_at": now.isoformat(),
        }
    else:
        membership.cancellation_info = {
            "cancelled_at": now.isoformat(),
            "reason": reason,
            "effective_at": membership.current_period_end.isoformat(),
            "pending": True,
        }

    await db.commit()
    await db.refresh(membership)

    if cancel_immediately:
        await _cancel_addon_memberships(db, membership)

    return membership


async def _cancel_addon_memberships(
    db: AsyncSession, base_membership: ClientMembership
) -> None:
    result = await db.execute(
        select(ClientMembership).where(
            ClientMembership.base_membership_id == base_membership.client_membership_id,
            ClientMembership.status.in_([MembershipStatus.active, MembershipStatus.paused]),
        )
    )
    addons = result.scalars().all()
    now = datetime.now(timezone.utc)
    for addon in addons:
        addon.status = MembershipStatus.cancelled
        addon.cancellation_info = {
            "cancelled_at": now.isoformat(),
            "reason": "Base membership cancelled",
            "effective_at": now.isoformat(),
        }
    if addons:
        await db.commit()


async def record_visit(
    db: AsyncSession, membership: ClientMembership, *, notes: str | None = None
) -> ClientMembership:
    if membership.status != MembershipStatus.active:
        raise ValueError("Can only record visits for active memberships")

    if membership.total_visits_remaining is not None:
        if membership.total_visits_remaining <= 0:
            raise ValueError("No visits remaining")
        membership.total_visits_remaining = membership.total_visits_remaining - 1

    membership.visits_used_this_period = membership.visits_used_this_period + 1
    await db.commit()
    await db.refresh(membership)
    return membership


async def deduct_visit(db: AsyncSession, membership: ClientMembership) -> ClientMembership:
    if membership.total_visits_remaining is not None:
        if membership.total_visits_remaining <= 0:
            raise ValueError("No visits remaining")
        membership.total_visits_remaining = membership.total_visits_remaining - 1
    membership.visits_used_this_period = membership.visits_used_this_period + 1
    await db.commit()
    await db.refresh(membership)
    return membership


async def reset_period_visits(
    db: AsyncSession, membership: ClientMembership
) -> ClientMembership:
    membership.visits_used_this_period = 0
    if membership.current_period_end:
        period_length = None
        if membership.current_period_start and membership.current_period_end:
            period_length = membership.current_period_end - membership.current_period_start
        membership.current_period_start = membership.current_period_end
        if period_length:
            membership.current_period_end = membership.current_period_start + period_length
    await db.commit()
    await db.refresh(membership)
    return membership


async def process_expired_memberships(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ClientMembership).where(
            ClientMembership.status == MembershipStatus.active,
            ClientMembership.expires_at.isnot(None),
            ClientMembership.expires_at <= now,
        )
    )
    expired = result.scalars().all()
    for membership in expired:
        membership.status = MembershipStatus.expired
    if expired:
        await db.commit()
    return len(expired)


async def process_pending_cancellations(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ClientMembership).where(
            ClientMembership.status.in_([MembershipStatus.active, MembershipStatus.paused]),
            ClientMembership.cancellation_info.isnot(None),
        )
    )
    memberships = result.scalars().all()
    cancelled_count = 0
    for membership in memberships:
        info = membership.cancellation_info or {}
        if info.get("pending"):
            effective_at_str = info.get("effective_at")
            if effective_at_str:
                effective_at = datetime.fromisoformat(effective_at_str)
                if effective_at <= now:
                    membership.status = MembershipStatus.cancelled
                    info["pending"] = False
                    membership.cancellation_info = info
                    cancelled_count += 1
                    await _cancel_addon_memberships(db, membership)
    if cancelled_count:
        await db.commit()
    return cancelled_count


async def process_period_resets(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ClientMembership).where(
            ClientMembership.status == MembershipStatus.active,
            ClientMembership.current_period_end.isnot(None),
            ClientMembership.current_period_end <= now,
            ClientMembership.expires_at > now,
        )
    )
    memberships = result.scalars().all()
    reset_count = 0
    for membership in memberships:
        await reset_period_visits(db, membership)
        reset_count += 1
    return reset_count
