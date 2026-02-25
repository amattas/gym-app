import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from gym_api.config import settings

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)


def render_template(template_name: str, **context) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)


def _smtp_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)


async def send_email(
    *,
    to: str,
    subject: str,
    html_body: str,
    from_email: str | None = None,
) -> bool:
    sender = from_email or settings.smtp_from_email

    if not _smtp_configured():
        logger.info("SMTP not configured — email logged: to=%s subject=%s", to, subject)
        return True

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Email sent: to=%s subject=%s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to=%s subject=%s", to, subject)
        return False


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


async def send_email_verification(*, to: str, verify_url: str) -> bool:
    html = render_template(
        "email_verification.html",
        verify_url=verify_url,
    )
    return await send_email(
        to=to,
        subject="Verify your email address",
        html_body=html,
    )
