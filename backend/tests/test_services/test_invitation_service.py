import hashlib

from gym_api.services.invitation_service import _hash_token


def test_hash_token_deterministic():
    token = "test-token-123"
    h1 = _hash_token(token)
    h2 = _hash_token(token)
    assert h1 == h2
    assert h1 == hashlib.sha256(token.encode()).hexdigest()


def test_hash_token_different_for_different_inputs():
    h1 = _hash_token("token-a")
    h2 = _hash_token("token-b")
    assert h1 != h2
