"""JWT authentication helpers and FastAPI dependencies."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.config import get_settings
from app.db import get_db


# PBKDF2-SHA256 hashing (stdlib, no C compiler needed)
def hash_password(password: str, salt: str | None = None) -> str:
    """Return a salted PBKDF2 hash encoded as 'salt$hash'."""
    salt = salt or secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a plaintext password against a stored 'salt$hash'."""
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(password, salt), stored)


def create_access_token(user: models.User) -> str:
    """Create a signed JWT for a user."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "school_id": user.school_id,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing authentication")
    payload = decode_token(creds.credentials)
    user = db.query(models.User).filter_by(id=payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    """Dependency factory to restrict an endpoint by role."""

    def _dep(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Requires role in {roles}")
        return user

    return _dep
