from datetime import timedelta
import pytest
import jwt

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    raw_pwd = "my-secret-password-123"
    hash1 = get_password_hash(raw_pwd)
    hash2 = get_password_hash(raw_pwd)

    # Hashes must differ due to unique salts
    assert hash1 != hash2

    # Verification must succeed for the correct password against both hashes
    assert verify_password(raw_pwd, hash1) is True
    assert verify_password(raw_pwd, hash2) is True

    # Verification must fail for incorrect passwords
    assert verify_password("wrong-password", hash1) is False


def test_create_and_decode_access_token():
    payload_data = {"sub": "user-uuid-12345", "role": "admin"}
    token = create_access_token(data=payload_data)

    decoded = decode_access_token(token)

    assert decoded["sub"] == "user-uuid-12345"
    assert decoded["role"] == "admin"
    assert "exp" in decoded


def test_expired_token_raises_expired_signature_error():
    payload_data = {"sub": "user-uuid-12345"}
    # Token expired 10 minutes ago
    expired_token = create_access_token(
        data=payload_data, expires_delta=timedelta(minutes=-10)
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)


def test_tampered_token_raises_jwt_error():
    payload_data = {"sub": "user-uuid-12345"}
    valid_token = create_access_token(data=payload_data)
    
    # Tamper with the token string
    tampered_token = valid_token[:-4] + "fake"

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered_token)