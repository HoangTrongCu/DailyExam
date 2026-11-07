"""Exam generation / fetch / status transitions."""

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.exam_composer import ICT, compose_exam


def _active_blueprint(db: Session, school_id: str) -> dict | None:
    row = (
        db.query(models.Blueprint)
        .filter_by(school_id=school_id, is_active=True)
        .order_by(models.Blueprint.version.desc())
        .first()
    )
    return row.structure if row else None


def generate_daily_exam(db: Session, school_id: str, exam_date: date) -> models.Exam:
    existing = db.query(models.Exam).filter_by(school_id=school_id, exam_date=exam_date).first()
    if existing:
        return existing
    school = db.query(models.School).filter_by(id=school_id).first()
    if not school:
        raise ValueError(f"Unknown school: {school_id}")
    bp = _active_blueprint(db, school_id)
    comp = compose_exam(school_id, exam_date, bp)
    row = models.Exam(
        id=comp.id,
        school_id=school_id,
        exam_date=exam_date,
        status="open",
        duration_minutes=comp.duration_minutes,
        exam_data={"questions": comp.questions},
        answer_key=comp.answer_key,
        answer_key_version=1,
        gate_open_at=comp.gate_open_at,
        gate_close_at=comp.gate_close_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_exams_for_date(db: Session, exam_date: date) -> list[models.Exam]:
    return db.query(models.Exam).filter_by(exam_date=exam_date).all()


def list_exams_this_week(db: Session) -> list[models.Exam]:
    today_ict = datetime.now(ICT).date()
    monday = today_ict.replace(day=today_ict.day - today_ict.weekday()) if today_ict.weekday() else today_ict
    return (
        db.query(models.Exam)
        .filter(models.Exam.exam_date >= monday)
        .filter(models.Exam.exam_date <= today_ict)
        .all()
    )


def public_view(exam: models.Exam) -> dict[str, Any]:
    """Exam view for student without answers."""
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


def transition_statuses(db: Session, now: datetime) -> dict[str, int]:
    """Called by scheduler: open → makeup → closed based on current time."""
    now_utc = now.astimezone(timezone.utc)
    moved_makeup = 0
    moved_closed = 0
    for exam in db.query(models.Exam).filter(models.Exam.status == "open").all():
        if now_utc >= exam.gate_close_at.replace(tzinfo=timezone.utc):
            exam.status = "makeup"
            moved_makeup += 1
    for exam in db.query(models.Exam).filter(models.Exam.status == "makeup").all():
        week_end = exam.gate_close_at.replace(tzinfo=timezone.utc)
        from datetime import timedelta
        days_to_sunday = (6 - exam.exam_date.weekday()) % 7
        close_forever = week_end + timedelta(days=days_to_sunday)
        if now_utc >= close_forever:
            exam.status = "closed"
            moved_closed += 1
    db.commit()
    return {"makeup": moved_makeup, "closed": moved_closed}
