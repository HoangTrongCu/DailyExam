"""User registration, approval, and lookup."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.auth import hash_password, verify_password


class AccountStatusError(ValueError):
    """Raised when a user cannot authenticate due to their account status."""

    def __init__(self, message: str, status: str) -> None:
        super().__init__(message)
        self.status = status


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    role: str = "student",
    school_id: str | None = None,
    grade: str | None = None,
    status: str = "pending",
) -> models.User:
    """Create a user; raise ValueError if email exists.

    By default new users are ``pending`` and must be approved by an admin
    before they can log in. Seed users may pass ``status='active'``.
    """
    existing = db.query(models.User).filter_by(email=email).first()
    if existing:
        raise ValueError("Email already registered")
    user = models.User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        status=status,
        school_id=school_id,
        grade=grade,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> models.User:
    """Return the user if credentials are valid, else raise AccountStatusError."""
    user = db.query(models.User).filter_by(email=email).first()
    if not user:
        raise AccountStatusError("Invalid email or password", "invalid")
    if not verify_password(password, user.password_hash):
        raise AccountStatusError("Invalid email or password", "invalid")
    if user.status == "pending":
        raise AccountStatusError(
            "Tài khoản của bạn đang chờ admin phê duyệt", "pending"
        )
    if user.status == "rejected":
        raise AccountStatusError("Tài khoản của bạn đã bị từ chối", "rejected")
    return user


def list_users_by_status(db: Session, status: str) -> list[models.User]:
    return (
        db.query(models.User)
        .filter_by(status=status)
        .order_by(models.User.created_at.desc())
        .all()
    )


def set_user_status(
    db: Session,
    user_id: str,
    new_status: str,
    approver_id: str | None = None,
) -> models.User:
    """Update a user's status; records approver and timestamp."""
    if new_status not in {"pending", "active", "rejected"}:
        raise ValueError(f"Invalid status: {new_status}")
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"User not found: {user_id}")
    user.status = new_status
    user.approved_at = datetime.now(timezone.utc) if new_status != "pending" else None
    user.approved_by = approver_id if new_status != "pending" else None
    db.commit()
    db.refresh(user)
    return user
