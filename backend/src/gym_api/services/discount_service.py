import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.discount_code import DiscountCode
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_discount_code(
    db: AsyncSession, *, gym_id: uuid.UUID, **kwargs
) -> DiscountCode:
    code = DiscountCode(gym_id=gym_id, **kwargs)
    db.add(code)
    await db.commit()
    await db.refresh(code)
    return code


async def get_discount_code(
    db: AsyncSession, gym_id: uuid.UUID, discount_code_id: uuid.UUID
) -> DiscountCode | None:
    result = await db.execute(
        select(DiscountCode).where(
            DiscountCode.discount_code_id == discount_code_id,
            DiscountCode.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_discount_codes(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    is_active: bool | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[DiscountCode], dict]:
    query = select(DiscountCode).where(DiscountCode.gym_id == gym_id)
    if is_active is not None:
        query = query.where(DiscountCode.is_active.is_(is_active))
    query = apply_cursor_pagination(
        query, order_column=DiscountCode.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_discount_code(
    db: AsyncSession, code: DiscountCode, **kwargs
) -> DiscountCode:
    for key, value in kwargs.items():
        if value is not None:
            setattr(code, key, value)
    await db.commit()
    await db.refresh(code)
    return code


async def delete_discount_code(db: AsyncSession, code: DiscountCode) -> None:
    await db.delete(code)
    await db.commit()


async def validate_discount_code(
    db: AsyncSession, gym_id: uuid.UUID, *, code_str: str, plan_type: str | None = None
) -> dict:
    result = await db.execute(
        select(DiscountCode).where(
            DiscountCode.gym_id == gym_id,
            DiscountCode.code == code_str,
            DiscountCode.is_active.is_(True),
        )
    )
    code = result.scalar_one_or_none()
    if not code:
        return {"valid": False, "message": "Invalid discount code"}

    now = datetime.now(timezone.utc)
    if code.valid_from and now < code.valid_from:
        return {"valid": False, "message": "Discount code not yet active"}
    if code.valid_until and now > code.valid_until:
        return {"valid": False, "message": "Discount code has expired"}
    if code.max_uses and code.times_used >= code.max_uses:
        return {"valid": False, "message": "Discount code has been fully redeemed"}
    if plan_type and code.applicable_plan_types:
        allowed = [t.strip() for t in code.applicable_plan_types.split(",")]
        if plan_type not in allowed:
            return {
                "valid": False,
                "message": "Discount code not applicable to this plan type",
            }

    return {
        "valid": True,
        "discount_type": code.discount_type.value,
        "amount": float(code.amount),
        "message": None,
    }


async def apply_discount(
    db: AsyncSession, gym_id: uuid.UUID, *, code_str: str, subtotal: int
) -> tuple[int, DiscountCode | None]:
    result = await db.execute(
        select(DiscountCode).where(
            DiscountCode.gym_id == gym_id,
            DiscountCode.code == code_str,
            DiscountCode.is_active.is_(True),
        )
    )
    code = result.scalar_one_or_none()
    if not code:
        return 0, None

    if code.discount_type.value == "percentage":
        discount = int(subtotal * float(code.amount) / 100)
    else:
        discount = int(float(code.amount) * 100)

    code.times_used += 1
    await db.commit()
    await db.refresh(code)
    return discount, code
