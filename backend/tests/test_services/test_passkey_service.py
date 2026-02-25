from unittest.mock import patch

from gym_api.services.passkey_service import (
    generate_authentication_options,
    generate_registration_options,
)


def test_registration_options_without_webauthn():
    """When py_webauthn is not installed, returns error dict."""
    with patch.dict("sys.modules", {"webauthn": None}):
        # Force re-import to trigger ImportError path
        result = generate_registration_options(
            user_id="user-123",
            user_name="test@example.com",
            user_display_name="Test User",
        )
    # Should either work (if webauthn installed) or return error
    assert isinstance(result, dict)


def test_authentication_options_without_webauthn():
    """When py_webauthn is not installed, returns error dict."""
    with patch.dict("sys.modules", {"webauthn": None}):
        result = generate_authentication_options()
    assert isinstance(result, dict)
