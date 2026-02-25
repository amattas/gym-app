import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import require_role
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.user import User, UserRole
from gym_api.schemas.invitation import (
    InvitationAcceptRequest,
    InvitationCreate,
    InvitationResponse,
)
from gym_api.services import auth_service, invitation_service
from gym_api.services.trainer_service import create_trainer

router = APIRouter(prefix="/v1/invitations", tags=["invitations"])


@router.post("", status_code=201, response_model=dict)
async def invite_trainer(
    body: InvitationCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    user: User = Depends(
        require_role(UserRole.gym_admin, UserRole.platform_admin)
    ),
    db: AsyncSession = Depends(get_db),
):
    invitation, raw_token = await invitation_service.create_invitation(
        db, gym_id=gym_id, email=body.email, invited_by=user.user_id
    )
    return {
        "data": {
            **InvitationResponse.model_validate(invitation).model_dump(
                mode="json"
            ),
            "setup_token": raw_token,
        }
    }


@router.post("/accept", response_model=dict)
async def accept_invitation(
    body: InvitationAcceptRequest,
    db: AsyncSession = Depends(get_db),
):
    invitation = await invitation_service.validate_invitation(db, body.token)
    if not invitation:
        raise HTTPException(
            status_code=400, detail="Invalid or expired invitation"
        )

    # Create user account for the trainer
    try:
        user = await auth_service.register_user(
            db,
            email=invitation.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
            role=UserRole.trainer,
            gym_id=invitation.gym_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Create trainer profile
    await create_trainer(
        db,
        gym_id=invitation.gym_id,
        user_id=user.user_id,
        first_name=body.first_name,
        last_name=body.last_name,
        email=invitation.email,
    )

    await invitation_service.accept_invitation(db, invitation)

    return {
        "data": {
            "user_id": str(user.user_id),
            "email": user.email,
            "role": user.role.value,
        }
    }
