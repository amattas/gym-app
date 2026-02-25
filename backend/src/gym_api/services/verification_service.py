import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.email_verification import EmailVerificationToken
from gym_api.models.password_reset import PasswordResetToken
from gym_api.services.password_service import generate_reset_token, hash_token

PASSWORD_RESET_EXPIRY_HOURS = 1
EMAIL_VERIFICATION_EXPIRY_HOURS = 24


async def create_password_reset_token(
    db: AsyncSession, user_id: uuid.UUID
) -> str:
    raw_token = generate_reset_token()
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def validate_password_reset_token(
    db: AsyncSession, raw_token: str
) -> PasswordResetToken | None:
    token_hash = hash_token(raw_token)
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()
    if not token:
        return None
    if token.is_used:
        return None
    if token.expires_at < datetime.now(timezone.utc):
        return None
    return token


async def consume_password_reset_token(
    db: AsyncSession, token: PasswordResetToken
) -> None:
    token.is_used = True
    await db.commit()


async def create_email_verification_token(
    db: AsyncSession, user_id: uuid.UUID
) -> str:
    raw_token = generate_reset_token()
    token = EmailVerificationToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def validate_email_verification_token(
    db: AsyncSession, raw_token: str
) -> EmailVerificationToken | None:
    token_hash = hash_token(raw_token)
    result = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        return None
    if token.is_used:
        return None
    if token.expires_at < datetime.now(timezone.utc):
        return None
    return token


async def consume_email_verification_token(
    db: AsyncSession, token: EmailVerificationToken
) -> None:
    token.is_used = True
    await db.commit()
