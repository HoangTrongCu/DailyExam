"""User registration and lookup."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from app.auth import hash_password, verify_password


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    role: str = "student",
    school_id: str | None = None,
    grade: str | None = None,
) -> models.User:
    """Create a user; raise ValueError if email exists."""
    existing = db.query(models.User).filter_by(email=email).first()
    if existing:
        raise ValueError("Email already registered")
    user = models.User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        school_id=school_id,
        grade=grade,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> models.User | None:
    user = db.query(models.User).filter_by(email=email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
