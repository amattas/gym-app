import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest

from gym_api.models.user import User, UserRole
from gym_api.services.auth_service import (
    create_access_token,
    decode_access_token,
)


def _make_user(**overrides) -> User:
    defaults = {
        "user_id": uuid.uuid4(),
        "email": "test@example.com",
        "role": UserRole.client,
        "gym_id": uuid.uuid4(),
        "first_name": "Test",
        "last_name": "User",
        "password_hash": "$argon2...",
        "is_active": True,
        "email_verified": False,
        "mfa_enabled": False,
        "mfa_secret": None,
        "backup_codes": None,
    }
    defaults.update(overrides)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


def test_create_access_token_structure():
    user = _make_user()
    token = create_access_token(user)
    payload = jwt.decode(token, options={"verify_signature": False})
    assert payload["sub"] == str(user.user_id)
    assert payload["email"] == user.email
    assert payload["role"] == "client"
    assert payload["gym_id"] == str(user.gym_id)
    assert "exp" in payload
    assert "iat" in payload


def test_access_token_roundtrip():
    user = _make_user()
    token = create_access_token(user)
    payload = decode_access_token(token)
    assert payload["sub"] == str(user.user_id)


def test_access_token_without_gym_id():
    user = _make_user(gym_id=None, role=UserRole.platform_admin)
    token = create_access_token(user)
    payload = decode_access_token(token)
    assert payload["gym_id"] is None


def test_expired_token_raises():
    user = _make_user()
    with patch("gym_api.services.auth_service.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        token = create_access_token(user)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_tampered_token_raises():
    user = _make_user()
    token = create_access_token(user)
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(Exception):
        decode_access_token(tampered)
