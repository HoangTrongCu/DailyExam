"""Tests for auth helpers."""

import pytest
from jose import jwt

from app import models
from app.auth import create_access_token, decode_token, hash_password, verify_password
from app.config import get_settings


def test_hash_and_verify_password() -> None:
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_hash_is_salted() -> None:
    a = hash_password("same")
    b = hash_password("same")
    assert a != b


def test_verify_malformed_hash() -> None:
    assert not verify_password("x", "nosaltnohash")


def test_create_and_decode_token() -> None:
    user = models.User(
        id="u1",
        email="a@b.c",
        full_name="A",
        password_hash="x",
        role="student",
        school_id="cau_giay",
    )
    token = create_access_token(user)
    data = decode_token(token)
    assert data["sub"] == "u1"
    assert data["role"] == "student"


def test_decode_invalid_token_raises() -> None:
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        decode_token("not-a-token")


def test_decode_tampered_token_raises() -> None:
    from fastapi import HTTPException
    settings = get_settings()
    token = jwt.encode({"sub": "x"}, "wrong-secret", algorithm=settings.jwt_algorithm)
    with pytest.raises(HTTPException):
        decode_token(token)
