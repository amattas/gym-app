from unittest.mock import AsyncMock, patch

import pytest

from tests.test_auth.helpers import make_mock_user

VALID_PASSWORD = "SecureP@ssw0rd123"


@pytest.mark.asyncio
async def test_register_success(client):
    user = make_mock_user(email="new@gym.com")

    with (
        patch("gym_api.routers.auth.auth_service.register_user", return_value=user),
        patch("gym_api.routers.auth.check_password_breach", return_value=False),
    ):
        resp = await client.post(
            "/v1/auth/register",
            json={
                "email": "new@gym.com",
                "password": VALID_PASSWORD,
                "first_name": "New",
                "last_name": "User",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["email"] == "new@gym.com"


@pytest.mark.asyncio
async def test_register_short_password(client):
    resp = await client.post(
        "/v1/auth/register",
        json={
            "email": "user@gym.com",
            "password": "Short1!",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert resp.status_code == 400
    assert "12 characters" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_register_missing_uppercase(client):
    resp = await client.post(
        "/v1/auth/register",
        json={
            "email": "user@gym.com",
            "password": "nouppercase1234!",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert resp.status_code == 400
    assert "uppercase" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_register_missing_special_char(client):
    resp = await client.post(
        "/v1/auth/register",
        json={
            "email": "user@gym.com",
            "password": "NoSpecialChar123",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert resp.status_code == 400
    assert "special character" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_register_breached_password(client):
    with patch("gym_api.routers.auth.check_password_breach", return_value=True):
        resp = await client.post(
            "/v1/auth/register",
            json={
                "email": "user@gym.com",
                "password": VALID_PASSWORD,
                "first_name": "A",
                "last_name": "B",
            },
        )
    assert resp.status_code == 400
    assert "breach" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    with (
        patch(
            "gym_api.routers.auth.auth_service.register_user",
            side_effect=ValueError("Email already registered"),
        ),
        patch("gym_api.routers.auth.check_password_breach", return_value=False),
    ):
        resp = await client.post(
            "/v1/auth/register",
            json={
                "email": "dup@gym.com",
                "password": VALID_PASSWORD,
                "first_name": "A",
                "last_name": "B",
            },
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    user = make_mock_user()

    with (
        patch("gym_api.routers.auth.auth_service.authenticate_user", return_value=user),
        patch("gym_api.routers.auth.auth_service.create_access_token", return_value="at"),
        patch("gym_api.routers.auth.auth_service.create_refresh_token", return_value="rt"),
        patch("gym_api.routers.auth.auth_service.create_session", return_value=AsyncMock()),
    ):
        resp = await client.post(
            "/v1/auth/login",
            json={"email": "user@gym.com", "password": "password123"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "at"
    assert body["refresh_token"] == "rt"
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    with patch("gym_api.routers.auth.auth_service.authenticate_user", return_value=None):
        resp = await client.post(
            "/v1/auth/login",
            json={"email": "bad@gym.com", "password": "wrong"},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_mfa_required(client):
    user = make_mock_user(mfa_enabled=True, mfa_secret="JBSWY3DPEHPK3PXP")

    with patch("gym_api.routers.auth.auth_service.authenticate_user", return_value=user):
        resp = await client.post(
            "/v1/auth/login",
            json={"email": "user@gym.com", "password": "password123"},
        )
    assert resp.status_code == 403
    assert "MFA" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_refresh_success(client):
    user = make_mock_user()

    with (
        patch(
            "gym_api.routers.auth.auth_service.rotate_refresh_token",
            return_value=(user, "new-refresh"),
        ),
        patch("gym_api.routers.auth.auth_service.create_access_token", return_value="new-access"),
    ):
        resp = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "old-refresh"},
        )
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "new-access"
    assert resp.json()["refresh_token"] == "new-refresh"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    with patch("gym_api.routers.auth.auth_service.rotate_refresh_token", return_value=None):
        resp = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "bad-token"},
        )
    assert resp.status_code == 401
