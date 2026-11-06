"""SQLAlchemy ORM models."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    grade_levels: Mapped[list[str]] = mapped_column(JSON, default=list)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # student / teacher / admin
    school_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("schools.id"), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    chuyen_de: Mapped[str] = mapped_column(String(50), nullable=False)
    dang_bai: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    scope: Mapped[str] = mapped_column(String(20), default="core")  # core or school
    school_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("schools.id"), nullable=True)
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class DailyExamRow(Base):
    __tablename__ = "daily_exams"
    __table_args__ = (UniqueConstraint("school_id", "exam_date", name="uq_school_date"),)

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    school_id: Mapped[str] = mapped_column(String(50), ForeignKey("schools.id"), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ready")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    exam_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    answer_key: Mapped[dict] = mapped_column(JSON, nullable=False)
    gate_open_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    gate_close_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("exam_id", "student_id", name="uq_exam_student"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    exam_id: Mapped[str] = mapped_column(String(100), ForeignKey("daily_exams.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    max_total_score: Mapped[float] = mapped_column(Float, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    question_results: Mapped[list] = mapped_column(JSON, default=list)
    graded_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Analytics(Base):
    """Rolling analytics per student+chuyen_de for strength/weakness insights."""
    __tablename__ = "analytics"
    __table_args__ = (UniqueConstraint("student_id", "chuyen_de", name="uq_student_cd"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    chuyen_de: Mapped[str] = mapped_column(String(50), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
