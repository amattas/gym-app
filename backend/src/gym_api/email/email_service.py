import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)


def render_template(template_name: str, **context) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)


async def send_email(
    *,
    to: str,
    subject: str,
    html_body: str,
    from_email: str = "noreply@gymplatform.io",
) -> bool:
    # In production, this would call Resend API
    # For MVP, log the email intent
    logger.info(
        "Email queued: to=%s subject=%s from=%s",
        to,
        subject,
        from_email,
    )
    return True


async def send_trainer_invitation(
    *, to: str, gym_name: str, setup_url: str
) -> bool:
    html = render_template(
        "trainer_invitation.html",
        gym_name=gym_name,
        setup_url=setup_url,
    )
    return await send_email(
        to=to,
        subject=f"You've been invited to join {gym_name}",
        html_body=html,
    )


async def send_password_reset(*, to: str, reset_url: str) -> bool:
    html = render_template(
        "password_reset.html",
        reset_url=reset_url,
    )
    return await send_email(
        to=to,
        subject="Reset your password",
        html_body=html,
    )
