import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from gym_api.dependencies.auth import get_current_user, require_role
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.models.user import UserRole
from gym_api.services.auth_service import create_access_token
from tests.test_auth.helpers import make_mock_user


@pytest.mark.asyncio
async def test_get_current_user_valid():
    user = make_mock_user()
    token = create_access_token(user)
    creds = MagicMock()
    creds.credentials = token

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_current_user(creds, mock_db)
    assert result.user_id == user.user_id


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    creds = MagicMock()
    creds.credentials = "bad.token.here"
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(creds, mock_db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_require_role_allowed():
    user = make_mock_user(role=UserRole.gym_admin)
    checker = require_role(UserRole.gym_admin, UserRole.platform_admin)
    result = await checker(user)
    assert result.role == UserRole.gym_admin


@pytest.mark.asyncio
async def test_require_role_denied():
    user = make_mock_user(role=UserRole.client)
    checker = require_role(UserRole.gym_admin)
    with pytest.raises(HTTPException) as exc_info:
        await checker(user)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_gym_context_returns_gym_id():
    gym_id = uuid.uuid4()
    user = make_mock_user(gym_id=gym_id, role=UserRole.trainer)
    result = await get_gym_context(user)
    assert result == gym_id


@pytest.mark.asyncio
async def test_gym_context_platform_admin_rejected():
    user = make_mock_user(role=UserRole.platform_admin, gym_id=None)
    with pytest.raises(HTTPException) as exc_info:
        await get_gym_context(user)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_gym_context_no_gym_rejected():
    user = make_mock_user(gym_id=None, role=UserRole.client)
    with pytest.raises(HTTPException) as exc_info:
        await get_gym_context(user)
    assert exc_info.value.status_code == 403
