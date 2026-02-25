import pyotp

from gym_api.services.mfa_service import (
    generate_backup_codes,
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
)


def test_generate_totp_secret():
    secret = generate_totp_secret()
    assert len(secret) > 10


def test_get_totp_uri():
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, "test@example.com")
    assert "otpauth://totp/" in uri
    assert "test%40example.com" in uri or "test@example.com" in uri
    assert "Gym%20App" in uri or "Gym+App" in uri


def test_verify_totp_valid():
    secret = generate_totp_secret()
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert verify_totp(secret, code) is True


def test_verify_totp_invalid():
    secret = generate_totp_secret()
    assert verify_totp(secret, "000000") is False


def test_generate_backup_codes():
    codes = generate_backup_codes()
    assert len(codes) == 8
    assert all(len(c) == 8 for c in codes)
    assert len(set(codes)) == 8


def test_generate_backup_codes_custom_count():
    codes = generate_backup_codes(count=4)
    assert len(codes) == 4
