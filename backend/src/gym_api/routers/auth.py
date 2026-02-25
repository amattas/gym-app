import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.models.user import User
from gym_api.services import auth_service
from gym_api.services.mfa_service import generate_totp_secret, get_totp_uri, verify_totp

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MFASetupResponse(BaseModel):
    secret: str
    uri: str


class MFAVerifyRequest(BaseModel):
    code: str


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    ip_address: str | None
    user_agent: str | None
    last_used_at: str
    created_at: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    try:
        user = await auth_service.register_user(
            db,
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"data": {"user_id": str(user.user_id), "email": user.email}}


@router.post("/login")
async def login(
    body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    user = await auth_service.authenticate_user(db, email=body.email, password=body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.mfa_enabled:
        if not body.mfa_code:
            raise HTTPException(status_code=403, detail="MFA code required")
        if not verify_totp(user.mfa_secret, body.mfa_code):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

    access_token = auth_service.create_access_token(user)
    refresh_token = await auth_service.create_refresh_token(db, user.user_id)

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    await auth_service.create_session(db, user.user_id, ip, ua)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.rotate_refresh_token(db, body.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user, new_refresh = result
    access_token = auth_service.create_access_token(user)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/mfa/setup")
async def mfa_setup(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    secret = generate_totp_secret()
    user.mfa_secret = secret
    await db.commit()
    uri = get_totp_uri(secret, user.email)
    return MFASetupResponse(secret=secret, uri=uri)


@router.post("/mfa/verify")
async def mfa_verify(
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")
    if not verify_totp(user.mfa_secret, body.code):
        raise HTTPException(status_code=401, detail="Invalid code")
    user.mfa_enabled = True
    await db.commit()
    return {"data": {"mfa_enabled": True}}


@router.get("/sessions")
async def list_sessions(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    sessions = await auth_service.list_sessions(db, user.user_id)
    return {
        "data": [
            SessionResponse(
                session_id=s.session_id,
                ip_address=s.ip_address,
                user_agent=s.user_agent,
                last_used_at=s.last_used_at.isoformat(),
                created_at=s.created_at.isoformat(),
            )
            for s in sessions
        ]
    }


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    revoked = await auth_service.revoke_session(db, user.user_id, session_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/sessions", status_code=204)
async def revoke_all_sessions(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    await auth_service.revoke_all_sessions(db, user.user_id)
