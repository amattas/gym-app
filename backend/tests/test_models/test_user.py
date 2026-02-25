from gym_api.models.user import User, UserRole


def test_user_instantiation():
    user = User(
        email="test@example.com",
        password_hash="$argon2...",
        first_name="Test",
        last_name="User",
        role=UserRole.client,
        is_active=True,
        email_verified=False,
        mfa_enabled=False,
    )
    assert user.email == "test@example.com"
    assert user.role == UserRole.client
    assert user.is_active is True
    assert user.mfa_enabled is False


def test_user_roles():
    assert UserRole.platform_admin.value == "platform_admin"
    assert UserRole.gym_admin.value == "gym_admin"
    assert UserRole.trainer.value == "trainer"
    assert UserRole.client.value == "client"
