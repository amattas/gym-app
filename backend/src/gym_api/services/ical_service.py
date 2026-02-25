import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.calendar_token import CalendarToken
from gym_api.models.schedule import Schedule, ScheduleStatus


async def generate_token(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    owner_type: str,
    owner_id: uuid.UUID,
) -> tuple[CalendarToken, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    existing = await db.execute(
        select(CalendarToken).where(
            CalendarToken.owner_type == owner_type,
            CalendarToken.owner_id == owner_id,
            CalendarToken.is_revoked.is_(False),
        )
    )
    for old in existing.scalars().all():
        old.is_revoked = True

    cal_token = CalendarToken(
        gym_id=gym_id,
        owner_type=owner_type,
        owner_id=owner_id,
        token_hash=token_hash,
    )
    db.add(cal_token)
    await db.commit()
    await db.refresh(cal_token)
    return cal_token, token


async def validate_token(
    db: AsyncSession, token: str
) -> CalendarToken | None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(CalendarToken).where(
            CalendarToken.token_hash == token_hash,
            CalendarToken.is_revoked.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def generate_ics(
    db: AsyncSession,
    owner_type: str,
    owner_id: uuid.UUID,
    *,
    hide_names: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)
    end = now + timedelta(days=90)

    if owner_type == "trainer":
        query = select(Schedule).where(
            Schedule.trainer_id == owner_id,
            Schedule.status.in_([ScheduleStatus.confirmed, ScheduleStatus.tentative]),
            Schedule.scheduled_start >= start,
            Schedule.scheduled_start <= end,
        )
    else:
        query = select(Schedule).where(
            Schedule.client_id == owner_id,
            Schedule.status.in_([ScheduleStatus.confirmed, ScheduleStatus.tentative]),
            Schedule.scheduled_start >= start,
            Schedule.scheduled_start <= end,
        )

    result = await db.execute(query)
    schedules = result.scalars().all()

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Gym API//EN",
    ]
    for s in schedules:
        summary = "Session" if hide_names else f"Session - {s.schedule_id}"
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{s.schedule_id}@gymapi",
            f"DTSTART:{s.scheduled_start.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{s.scheduled_end.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{summary}",
            "STATUS:{}".format(
                s.status.value.upper() if hasattr(s.status, "value") else str(s.status).upper()
            ),
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
