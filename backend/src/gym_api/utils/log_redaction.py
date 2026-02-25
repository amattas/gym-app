import logging
import re

EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9_.+-])([a-zA-Z0-9_.+-]*)@([a-zA-Z0-9-]+\.[a-zA-Z]{2,})")
PHONE_PATTERN = re.compile(r"\b(\d{3}[-.\s]?)(\d{3}[-.\s]?\d{4})\b")
TOKEN_PATTERN = re.compile(r"(Bearer\s+|token[=:]\s*)[A-Za-z0-9_\-\.]+", re.IGNORECASE)

SENSITIVE_FIELDS = {"password", "secret", "token", "api_key", "authorization"}


def redact_email(match: re.Match) -> str:
    first_char = match.group(1)
    domain = match.group(3)
    return f"{first_char}***@{domain}"


def redact_phone(match: re.Match) -> str:
    return match.group(1) + "***-****"


def redact_token(match: re.Match) -> str:
    prefix = match.group(1)
    return prefix + "[REDACTED]"


def redact_string(text: str) -> str:
    text = EMAIL_PATTERN.sub(redact_email, text)
    text = PHONE_PATTERN.sub(redact_phone, text)
    text = TOKEN_PATTERN.sub(redact_token, text)
    return text


class PiiRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_string(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: redact_string(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_string(str(a)) for a in record.args)
        return True
