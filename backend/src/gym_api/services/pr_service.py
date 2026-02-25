import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.personal_record import PersonalRecord, PRType

PR_REP_THRESHOLDS = {
    1: PRType.one_rm,
    3: PRType.three_rm,
    5: PRType.five_rm,
    10: PRType.ten_rm,
}


def detect_rep_prs(
    weight_kg: float, reps: int
) -> list[tuple[PRType, float, int]]:
    results = []
    for threshold, pr_type in PR_REP_THRESHOLDS.items():
        if reps <= threshold:
            results.append((pr_type, weight_kg, threshold))
    return results


def calculate_volume(sets: list[dict]) -> float:
    total = 0.0
    for s in sets:
        w = s.get("weight_kg") or 0
        r = s.get("reps") or 0
        if s.get("completed", True):
            total += w * r
    return total


async def check_and_record_prs(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    exercise_id: uuid.UUID,
    exercise_name: str,
    weight_kg: float,
    reps: int,
    sets_data: list[dict] | None = None,
) -> list[PersonalRecord]:
    new_prs = []

    # Check rep-based PRs
    candidates = detect_rep_prs(weight_kg, reps)
    for pr_type, w, r in candidates:
        existing = await db.execute(
            select(PersonalRecord).where(
                PersonalRecord.client_id == client_id,
                PersonalRecord.exercise_id == exercise_id,
                PersonalRecord.pr_type == pr_type,
            ).order_by(PersonalRecord.weight_kg.desc()).limit(1)
        )
        current_best = existing.scalar_one_or_none()
        if not current_best or w > float(current_best.weight_kg or 0):
            pr = PersonalRecord(
                gym_id=gym_id,
                client_id=client_id,
                exercise_id=exercise_id,
                pr_type=pr_type,
                weight_kg=w,
                reps=r,
                exercise_name=exercise_name,
                achieved_at=datetime.now(timezone.utc),
            )
            db.add(pr)
            new_prs.append(pr)

    # Check volume PR
    if sets_data:
        volume = calculate_volume(sets_data)
        if volume > 0:
            existing_vol = await db.execute(
                select(PersonalRecord).where(
                    PersonalRecord.client_id == client_id,
                    PersonalRecord.exercise_id == exercise_id,
                    PersonalRecord.pr_type == PRType.volume,
                ).order_by(PersonalRecord.volume_kg.desc()).limit(1)
            )
            current_best_vol = existing_vol.scalar_one_or_none()
            if not current_best_vol or volume > float(
                current_best_vol.volume_kg or 0
            ):
                pr = PersonalRecord(
                    gym_id=gym_id,
                    client_id=client_id,
                    exercise_id=exercise_id,
                    pr_type=PRType.volume,
                    volume_kg=volume,
                    exercise_name=exercise_name,
                    achieved_at=datetime.now(timezone.utc),
                )
                db.add(pr)
                new_prs.append(pr)

    if new_prs:
        await db.commit()
        for pr in new_prs:
            await db.refresh(pr)

    return new_prs


async def list_prs(
    db: AsyncSession,
    client_id: uuid.UUID,
    *,
    exercise_id: uuid.UUID | None = None,
) -> list[PersonalRecord]:
    query = select(PersonalRecord).where(
        PersonalRecord.client_id == client_id
    )
    if exercise_id:
        query = query.where(PersonalRecord.exercise_id == exercise_id)
    query = query.order_by(PersonalRecord.achieved_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
