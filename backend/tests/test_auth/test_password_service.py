from gym_api.services.password_service import (
    generate_reset_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_hash_and_verify():
    pwd = "my-secret-password"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True


def test_wrong_password():
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


def test_generate_reset_token_is_unique():
    t1 = generate_reset_token()
    t2 = generate_reset_token()
    assert t1 != t2
    assert len(t1) > 20


def test_hash_token_deterministic():
    token = "some-token"
    assert hash_token(token) == hash_token(token)
    assert hash_token("a") != hash_token("b")
