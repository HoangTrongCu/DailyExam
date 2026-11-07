"""User registration, auth, email-verify, password-reset, deletion."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app import models
from app.auth import hash_password, new_session_token, new_short_token, verify_password
from app.config import get_settings


class AuthError(ValueError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


def register_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    child_name: str,
    role: str = "student",
    status: str = "pending_verify",
) -> tuple[models.User, str | None]:
    """Create user; returns (user, verify_token). verify_token is None if status='active'."""
    if db.query(models.User).filter_by(email=email).first():
        raise AuthError("Email đã được đăng ký", "email_exists")
    user = models.User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        child_name=child_name,
        role=role,
        status=status,
    )
    db.add(user)
    db.flush()
    verify_token: str | None = None
    if status == "pending_verify":
        verify_token = _issue_verify_token(db, user.id, "verify_email")
    db.commit()
    db.refresh(user)
    return user, verify_token


def _issue_verify_token(db: Session, user_id: str, kind: str) -> str:
    settings = get_settings()
    hours = settings.verify_token_expire_hours if kind == "verify_email" else 0
    minutes = 0 if kind == "verify_email" else settings.reset_token_expire_minutes
    expires = datetime.now(timezone.utc) + timedelta(hours=hours, minutes=minutes)
    token = new_short_token()
    db.add(models.VerifyToken(token=token, user_id=user_id, kind=kind, expires_at=expires))
    return token


def verify_email_token(db: Session, token: str) -> models.User:
    row = db.query(models.VerifyToken).filter_by(token=token, kind="verify_email").first()
    if not row:
        raise AuthError("Link không hợp lệ", "invalid_token")
    if row.used:
        raise AuthError("Link đã được sử dụng", "used_token")
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise AuthError("Link đã hết hạn", "expired_token")
    user = db.query(models.User).filter_by(id=row.user_id).first()
    if not user:
        raise AuthError("User not found", "not_found")
    user.status = "active"
    user.email_verified_at = datetime.now(timezone.utc)
    row.used = True
    db.commit()
    db.refresh(user)
    return user


def authenticate_and_rotate_session(db: Session, email: str, password: str) -> tuple[models.User, str]:
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Email hoặc mật khẩu sai", "invalid_credentials")
    if user.status == "pending_verify":
        raise AuthError("Vui lòng xác minh email trước khi đăng nhập", "pending_verify")
    if user.status == "banned":
        raise AuthError("Tài khoản của bạn đã bị tạm khoá", "banned")
    if user.status == "deleted":
        raise AuthError("Tài khoản đã bị xoá", "deleted")
    new_token = new_session_token()
    user.session_token = new_token
    db.commit()
    db.refresh(user)
    return user, new_token


def request_password_reset(db: Session, email: str) -> str | None:
    user = db.query(models.User).filter_by(email=email).first()
    if not user:
        return None
    token = _issue_verify_token(db, user.id, "reset_password")
    db.commit()
    return token


def reset_password(db: Session, token: str, new_password: str) -> models.User:
    row = db.query(models.VerifyToken).filter_by(token=token, kind="reset_password").first()
    if not row:
        raise AuthError("Link không hợp lệ", "invalid_token")
    if row.used:
        raise AuthError("Link đã được sử dụng", "used_token")
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise AuthError("Link đã hết hạn", "expired_token")
    user = db.query(models.User).filter_by(id=row.user_id).first()
    if not user:
        raise AuthError("User not found", "not_found")
    user.password_hash = hash_password(new_password)
    user.session_token = None  # force re-login
    row.used = True
    db.commit()
    db.refresh(user)
    return user


def soft_delete(db: Session, user_id: str) -> None:
    user = db.query(models.User).filter_by(id=user_id).first()
    if user:
        user.status = "deleted"
        user.deleted_at = datetime.now(timezone.utc)
        user.session_token = None
        db.commit()
