
from gym_api.email.email_service import (
    render_template,
    send_email,
    send_password_reset,
    send_trainer_invitation,
)


def test_render_trainer_invitation_template():
    html = render_template(
        "trainer_invitation.html",
        gym_name="TestGym",
        setup_url="https://example.com/setup",
    )
    assert "TestGym" in html
    assert "https://example.com/setup" in html


def test_render_password_reset_template():
    html = render_template(
        "password_reset.html",
        reset_url="https://example.com/reset",
    )
    assert "https://example.com/reset" in html


async def test_send_email_returns_true():
    result = await send_email(
        to="user@example.com",
        subject="Test",
        html_body="<p>Hello</p>",
    )
    assert result is True


async def test_send_trainer_invitation():
    result = await send_trainer_invitation(
        to="trainer@example.com",
        gym_name="FitGym",
        setup_url="https://example.com/setup/abc",
    )
    assert result is True


async def test_send_password_reset():
    result = await send_password_reset(
        to="user@example.com",
        reset_url="https://example.com/reset/xyz",
    )
    assert result is True
