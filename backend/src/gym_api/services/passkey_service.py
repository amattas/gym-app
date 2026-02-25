import json
import logging
import os
from base64 import urlsafe_b64encode

logger = logging.getLogger(__name__)

RP_ID = os.getenv("WEBAUTHN_RP_ID", "localhost")
RP_NAME = os.getenv("WEBAUTHN_RP_NAME", "Gym Platform")
ORIGIN = os.getenv("WEBAUTHN_ORIGIN", "http://localhost:3000")


def generate_registration_options(
    *,
    user_id: str,
    user_name: str,
    user_display_name: str,
) -> dict:
    try:
        from webauthn import generate_registration_options as webauthn_reg
        from webauthn.helpers.structs import (
            AuthenticatorSelectionCriteria,
            ResidentKeyRequirement,
            UserVerificationRequirement,
        )

        options = webauthn_reg(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=user_id.encode(),
            user_name=user_name,
            user_display_name=user_display_name,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
        )
        return {
            "challenge": urlsafe_b64encode(options.challenge).decode(),
            "rp": {"id": options.rp.id, "name": options.rp.name},
            "user": {
                "id": urlsafe_b64encode(options.user.id).decode(),
                "name": options.user.name,
                "displayName": options.user.display_name,
            },
            "pubKeyCredParams": [
                {"type": p.type, "alg": p.alg} for p in options.pub_key_cred_params
            ],
            "timeout": options.timeout,
            "attestation": options.attestation,
        }
    except ImportError:
        logger.warning("py_webauthn not installed, passkey registration unavailable")
        return {"error": "WebAuthn not available"}


def generate_authentication_options(*, credential_ids: list[bytes] | None = None) -> dict:
    try:
        from webauthn import generate_authentication_options as webauthn_auth
        from webauthn.helpers.structs import PublicKeyCredentialDescriptor

        allow_credentials = []
        if credential_ids:
            allow_credentials = [
                PublicKeyCredentialDescriptor(id=cid) for cid in credential_ids
            ]

        options = webauthn_auth(
            rp_id=RP_ID,
            allow_credentials=allow_credentials,
        )
        return {
            "challenge": urlsafe_b64encode(options.challenge).decode(),
            "rpId": options.rp_id,
            "timeout": options.timeout,
            "allowCredentials": [
                {
                    "id": urlsafe_b64encode(c.id).decode(),
                    "type": c.type,
                }
                for c in options.allow_credentials
            ],
        }
    except ImportError:
        logger.warning("py_webauthn not installed, passkey auth unavailable")
        return {"error": "WebAuthn not available"}


def verify_registration_response(
    *,
    credential: dict,
    expected_challenge: bytes,
    expected_origin: str = ORIGIN,
    expected_rp_id: str = RP_ID,
) -> dict | None:
    try:
        from webauthn import verify_registration_response as webauthn_verify
        from webauthn.helpers.structs import RegistrationCredential

        verification = webauthn_verify(
            credential=RegistrationCredential.parse_raw(json.dumps(credential)),
            expected_challenge=expected_challenge,
            expected_origin=expected_origin,
            expected_rp_id=expected_rp_id,
        )
        return {
            "credential_id": urlsafe_b64encode(verification.credential_id).decode(),
            "credential_public_key": urlsafe_b64encode(
                verification.credential_public_key
            ).decode(),
            "sign_count": verification.sign_count,
        }
    except ImportError:
        logger.warning("py_webauthn not installed")
        return None
    except Exception as e:
        logger.error("Registration verification failed: %s", e)
        return None
