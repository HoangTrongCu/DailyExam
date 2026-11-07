"""Appeal management + regrade trigger."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.services.submission_service import regrade_all_for_exam


def file_appeal(db: Session, submission_id: str, student_id: str, question_id: str, reason: str) -> models.Appeal:
    sub = db.query(models.Submission).filter_by(id=submission_id, student_id=student_id).first()
    if not sub:
        raise ValueError("Submission not found")
    # Avoid duplicate open appeals
    existing = (
        db.query(models.Appeal)
        .filter_by(submission_id=submission_id, question_id=question_id, status="open")
        .first()
    )
    if existing:
        return existing
    ap = models.Appeal(
        submission_id=submission_id,
        student_id=student_id,
        question_id=question_id,
        reason=reason,
        status="open",
    )
    db.add(ap)
    db.commit()
    db.refresh(ap)
    return ap


def list_open_appeals(db: Session) -> list[models.Appeal]:
    return (
        db.query(models.Appeal)
        .filter_by(status="open")
        .order_by(models.Appeal.created_at)
        .all()
    )


def resolve_appeal(
    db: Session,
    appeal_id: str,
    action: str,  # 'accept' or 'reject'
    admin_note: str | None = None,
    new_correct: str | None = None,
) -> dict:
    ap = db.query(models.Appeal).filter_by(id=appeal_id).first()
    if not ap:
        raise ValueError("Appeal not found")
    if ap.status != "open":
        raise ValueError("Appeal already resolved")
    ap.admin_note = admin_note
    ap.resolved_at = datetime.now(timezone.utc)

    if action == "reject":
        ap.status = "rejected"
        db.commit()
        return {"status": "rejected", "regraded": 0}

    if action != "accept":
        raise ValueError("Invalid action")

    ap.status = "accepted"
    sub = db.query(models.Submission).filter_by(id=ap.submission_id).first()
    if not sub:
        raise ValueError("Submission missing")
    exam = db.query(models.Exam).filter_by(id=sub.exam_id).first()
    if not exam:
        raise ValueError("Exam missing")

    if new_correct is not None:
        key = exam.answer_key
        if ap.question_id in key:
            key[ap.question_id]["correct"] = new_correct
            exam.answer_key = key
            exam.answer_key_version += 1
            # Mark it dirty for SQLAlchemy JSON mutation
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(exam, "answer_key")

    db.commit()
    stats = regrade_all_for_exam(db, exam)
    return {"status": "accepted", **stats}


def disable_question(db: Session, exam_id: str, question_id: str) -> dict:
    """EC-9: mark a question as disabled; regrade exam."""
    exam = db.query(models.Exam).filter_by(id=exam_id).first()
    if not exam:
        raise ValueError("Exam not found")
    key = exam.answer_key
    if question_id not in key:
        raise ValueError("Question not in answer key")
    key[question_id]["disabled"] = True
    exam.answer_key = key
    exam.answer_key_version += 1
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(exam, "answer_key")
    db.commit()
    return regrade_all_for_exam(db, exam)
