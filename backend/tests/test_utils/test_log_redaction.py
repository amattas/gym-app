import logging

from gym_api.utils.log_redaction import PiiRedactionFilter, redact_string


def test_redact_email():
    result = redact_string("User john.doe@example.com signed in")
    assert "john.doe@example.com" not in result
    assert "j***@example.com" in result


def test_redact_phone():
    result = redact_string("Call 555-123-4567 for info")
    assert "123-4567" not in result
    assert "***-****" in result


def test_redact_bearer_token():
    result = redact_string("Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig")
    assert "eyJhbGci" not in result
    assert "[REDACTED]" in result


def test_no_false_positive_on_normal_text():
    text = "Hello world, this is a normal message"
    assert redact_string(text) == text


def test_pii_filter_on_log_record():
    filt = PiiRedactionFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="User admin@gym.com logged in",
        args=None,
        exc_info=None,
    )
    filt.filter(record)
    assert "admin@gym.com" not in record.msg
    assert "a***@gym.com" in record.msg


def test_pii_filter_with_args():
    filt = PiiRedactionFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Login for %s",
        args=("user@example.com",),
        exc_info=None,
    )
    filt.filter(record)
    assert "user@example.com" not in str(record.args)
