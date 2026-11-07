"""Auth helpers + config + email."""

import pytest
from jose import jwt

from app import models
from app.auth import (
    create_access_token,
    decode_token,
    hash_password,
    new_session_token,
    new_short_token,
    verify_password,
)
from app.config import Settings, get_settings
from app.services import email_service


class TestPassword:
    def test_roundtrip(self):
        h = hash_password("secret")
        assert verify_password("secret", h)
        assert not verify_password("wrong", h)

    def test_salted(self):
        assert hash_password("same") != hash_password("same")

    def test_malformed_hash(self):
        assert not verify_password("x", "nosalt")


class TestJWT:
    def test_roundtrip(self):
        user = models.User(id="u1", email="a@b.c", full_name="A", password_hash="x", role="student")
        tok = create_access_token(user, "st")
        d = decode_token(tok)
        assert d["sub"] == "u1" and d["st"] == "st"

    def test_bad_token_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            decode_token("not-a-jwt")

    def test_tampered(self):
        from fastapi import HTTPException
        s = get_settings()
        bad = jwt.encode({"sub": "x"}, "wrong-secret", algorithm=s.jwt_algorithm)
        with pytest.raises(HTTPException):
            decode_token(bad)

    def test_random_tokens_unique(self):
        assert new_session_token() != new_session_token()
        assert new_short_token() != new_short_token()


class TestConfig:
    def test_defaults(self):
        s = Settings()
        assert s.app_name == "DailyExam API"
        assert s.jwt_expire_minutes > 0


class TestEmail:
    def test_build_verify(self):
        subj, html = email_service.build_verify_email("PH", "http://x/v/t")
        assert "xác minh" in subj.lower() or "verify" in subj.lower()
        assert "http://x/v/t" in html

    def test_build_reset(self):
        subj, html = email_service.build_reset_email("PH", "http://x/r/t")
        assert "http://x/r/t" in html

    def test_build_result(self):
        subj, html = email_service.build_result_email("PH", "Con", "cau_giay", 7.5, 10.0, "http://x")
        assert "Con" in html and "7.5" in html

    def test_send_mock(self):
        email_service.reset_backend()
        assert email_service.send_email("a@b.c", "s", "<p>h</p>")
        assert email_service.get_backend().sent[-1].to == "a@b.c"
