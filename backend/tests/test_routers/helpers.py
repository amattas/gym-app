import uuid
from types import SimpleNamespace

from gym_api.models.user import UserRole


def make_mock_user(**overrides):
    defaults = dict(
        user_id=uuid.uuid4(),
        email="user@gym.com",
        password_hash="$argon2...",
        role=UserRole.gym_admin,
        gym_id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        is_active=True,
        email_verified=False,
        mfa_enabled=False,
        mfa_secret=None,
        backup_codes=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)
