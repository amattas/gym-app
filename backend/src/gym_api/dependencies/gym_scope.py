import uuid

from fastapi import Depends, HTTPException, status

from gym_api.dependencies.auth import get_current_user
from gym_api.models.user import User, UserRole


async def get_gym_context(user: User = Depends(get_current_user)) -> uuid.UUID:
    if user.role == UserRole.platform_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform admin must specify gym_id explicitly",
        )
    if not user.gym_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any gym",
        )
    return user.gym_id
