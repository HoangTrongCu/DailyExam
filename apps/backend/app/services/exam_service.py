"""Service for daily exam generation and lookup."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.exam_composer import compose_exam
from app.template_engine import load_all_templates


def ensure_templates_loaded() -> int:
    """Lazy-load templates on first use."""
    return load_all_templates()


def generate_daily_exam(session: Session, school_id: str, exam_date: date) -> models.DailyExamRow:
    """Generate (or return existing) daily exam for a school/date."""
    ensure_templates_loaded()
    existing = (
        session.query(models.DailyExamRow)
        .filter_by(school_id=school_id, exam_date=exam_date)
        .first()
    )
    if existing:
        return existing

    school = session.query(models.School).filter_by(id=school_id).first()
    if not school:
        raise ValueError(f"Unknown school: {school_id}")
    config = school.config or {}

    composition = compose_exam(
        school_id=school_id,
        exam_date=exam_date,
        num_questions=config.get("num_questions", 10),
        duration_minutes=config.get("duration_minutes", 60),
        config=config,
    )
    row = models.DailyExamRow(
        id=composition.id,
        school_id=school_id,
        exam_date=exam_date,
        status="ready",
        duration_minutes=composition.duration_minutes,
        exam_data={"questions": composition.questions},
        answer_key=composition.answer_key,
        gate_open_at=composition.gate_open_at,
        gate_close_at=composition.gate_close_at,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def get_daily_exam(session: Session, school_id: str, exam_date: date) -> models.DailyExamRow | None:
    return (
        session.query(models.DailyExamRow)
        .filter_by(school_id=school_id, exam_date=exam_date)
        .first()
    )


def public_view(exam: models.DailyExamRow) -> dict[str, Any]:
    """Return exam without answer key (for student-facing responses)."""
    return {
        "id": exam.id,
        "school_id": exam.school_id,
        "exam_date": exam.exam_date.isoformat(),
        "status": exam.status,
        "duration_minutes": exam.duration_minutes,
        "questions": exam.exam_data.get("questions", []),
        "gate_open_at": exam.gate_open_at.isoformat(),
        "gate_close_at": exam.gate_close_at.isoformat(),
    }
