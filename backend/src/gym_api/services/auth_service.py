import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.config import settings
from gym_api.models.refresh_token import RefreshToken
from gym_api.models.session import UserSession
from gym_api.models.user import User, UserRole
from gym_api.services.password_service import hash_password, verify_password

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_refresh(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role.value,
        "gym_id": str(user.gym_id) if user.gym_id else None,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


async def register_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole = UserRole.client,
    gym_id: uuid.UUID | None = None,
) -> User:
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        gym_id=gym_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def create_refresh_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    raw_token = secrets.token_urlsafe(48)
    family_id = uuid.uuid4()
    token = RefreshToken(
        user_id=user_id,
        token_hash=_hash_refresh(raw_token),
        family_id=family_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> tuple[User, str] | None:
    token_hash = _hash_refresh(raw_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()

    if not stored or stored.is_revoked:
        if stored:
            await _revoke_family(db, stored.family_id)
        return None

    if stored.expires_at < datetime.now(timezone.utc):
        return None

    stored.is_revoked = True

    user_result = await db.execute(select(User).where(User.user_id == stored.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        return None

    new_raw = secrets.token_urlsafe(48)
    new_token = RefreshToken(
        user_id=user.user_id,
        token_hash=_hash_refresh(new_raw),
        family_id=stored.family_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_token)
    await db.commit()
    return user, new_raw


async def _revoke_family(db: AsyncSession, family_id: uuid.UUID):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id, RefreshToken.is_revoked.is_(False)
        )
    )
    for token in result.scalars():
        token.is_revoked = True
    await db.commit()


async def create_session(
    db: AsyncSession, user_id: uuid.UUID, ip: str | None, user_agent: str | None
) -> UserSession:
    session = UserSession(user_id=user_id, ip_address=ip, user_agent=user_agent)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def list_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[UserSession]:
    result = await db.execute(
        select(UserSession).where(UserSession.user_id == user_id).order_by(
            UserSession.last_used_at.desc()
        )
    )
    return list(result.scalars().all())


async def revoke_session(db: AsyncSession, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(UserSession).where(
            UserSession.session_id == session_id, UserSession.user_id == user_id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return False
    await db.delete(session)
    await db.commit()
    return True


async def revoke_all_sessions(
    db: AsyncSession, user_id: uuid.UUID, except_session_id: uuid.UUID | None = None
):
    result = await db.execute(select(UserSession).where(UserSession.user_id == user_id))
    for session in result.scalars():
        if except_session_id and session.session_id == except_session_id:
            continue
        await db.delete(session)
    await db.commit()
