"""ORM models per SDD §2."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    short_name: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Blueprint(Base):
    __tablename__ = "blueprints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    school_id: Mapped[str] = mapped_column(String(50), ForeignKey("schools.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    structure: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200))
    child_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student")  # student | admin
    status: Mapped[str] = mapped_column(String(20), default="pending_verify")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    session_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (UniqueConstraint("school_id", "exam_date", name="uq_school_date"),)

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    school_id: Mapped[str] = mapped_column(String(50), ForeignKey("schools.id"), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | makeup | closed
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    exam_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    answer_key: Mapped[dict] = mapped_column(JSON, nullable=False)
    answer_key_version: Mapped[int] = mapped_column(Integer, default=1)
    gate_open_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    gate_close_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("exam_id", "student_id", name="uq_exam_student"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    exam_id: Mapped[str] = mapped_column(String(100), ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    max_total_score: Mapped[float] = mapped_column(Float, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    question_results: Mapped[list] = mapped_column(JSON, default=list)
    answer_key_version_at_grade: Mapped[int] = mapped_column(Integer, default=1)
    counts_for_ranking: Mapped[bool] = mapped_column(Boolean, default=True)
    graded_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Appeal(Base):
    __tablename__ = "appeals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("submissions.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | accepted | rejected
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Analytics(Base):
    __tablename__ = "analytics"
    __table_args__ = (
        UniqueConstraint("student_id", "chuyen_de", "school_id", name="uq_stu_cd_school"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    chuyen_de: Mapped[str] = mapped_column(String(50), nullable=False)
    school_id: Mapped[str] = mapped_column(String(50), ForeignKey("schools.id"), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class EmailLog(Base):
    __tablename__ = "email_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class VerifyToken(Base):
    __tablename__ = "verify_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(20))  # verify_email | reset_password
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
