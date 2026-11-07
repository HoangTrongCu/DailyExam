"""Submission + grading + analytics + regrade."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.grader import grade_question


def submit_and_grade(db: Session, exam: models.Exam, student: models.User, answers: dict[str, str]) -> models.Submission:
    """Idempotent: if submission exists, return it."""
    existing = db.query(models.Submission).filter_by(exam_id=exam.id, student_id=student.id).first()
    if existing:
        return existing
    counts_for_rank = exam.status == "open"
    submission = _grade_and_persist(db, exam, student.id, answers, counts_for_rank)
    return submission


def _grade_and_persist(db: Session, exam: models.Exam, student_id: str, answers: dict[str, str], counts_for_rank: bool) -> models.Submission:
    questions = exam.exam_data.get("questions", [])
    answer_key = exam.answer_key or {}
    results = []
    total = 0.0
    max_total = 0.0
    for q in questions:
        ans = answers.get(q["id"], "")
        ref = answer_key.get(q["id"], {})
        r = grade_question(q, ans, ref)
        results.append({**r.__dict__, "chuyen_de": q.get("chuyen_de"), "type": q.get("type")})
        total += r.score
        max_total += r.max_score
    pct = round((total / max_total * 100) if max_total else 0.0, 2)
    submission = models.Submission(
        exam_id=exam.id,
        student_id=student_id,
        answers=answers,
        total_score=round(total, 2),
        max_total_score=round(max_total, 2),
        percentage=pct,
        question_results=results,
        answer_key_version_at_grade=exam.answer_key_version,
        counts_for_ranking=counts_for_rank,
        graded_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    _update_analytics(db, student_id, exam.school_id, results)
    db.commit()
    db.refresh(submission)
    return submission


def _update_analytics(db: Session, student_id: str, school_id: str, results: list[dict]) -> None:
    for r in results:
        cd = r.get("chuyen_de")
        if not cd:
            continue
        row = db.query(models.Analytics).filter_by(student_id=student_id, chuyen_de=cd, school_id=school_id).first()
        if not row:
            row = models.Analytics(student_id=student_id, chuyen_de=cd, school_id=school_id)
            db.add(row)
            db.flush()
        row.attempts = (row.attempts or 0) + 1
        if r.get("is_correct"):
            row.correct = (row.correct or 0) + 1
        row.total_score = (row.total_score or 0.0) + float(r.get("score", 0))
        row.max_score = (row.max_score or 0.0) + float(r.get("max_score", 0))


def regrade_all_for_exam(db: Session, exam: models.Exam) -> dict[str, int]:
    """After admin accepts an appeal and updates the answer key.
    Re-grade every submission on this exam; return count changed.
    """
    submissions = db.query(models.Submission).filter_by(exam_id=exam.id).all()
    changed = 0
    for sub in submissions:
        old_total = sub.total_score
        # Reset analytics contribution from old results
        _rollback_analytics(db, sub)
        # Re-grade
        questions = exam.exam_data.get("questions", [])
        answer_key = exam.answer_key or {}
        results = []
        total = 0.0
        max_total = 0.0
        for q in questions:
            ans = sub.answers.get(q["id"], "")
            ref = answer_key.get(q["id"], {})
            r = grade_question(q, ans, ref)
            results.append({**r.__dict__, "chuyen_de": q.get("chuyen_de"), "type": q.get("type")})
            total += r.score
            max_total += r.max_score
        sub.question_results = results
        sub.total_score = round(total, 2)
        sub.max_total_score = round(max_total, 2)
        sub.percentage = round((total / max_total * 100) if max_total else 0.0, 2)
        sub.answer_key_version_at_grade = exam.answer_key_version
        if abs(sub.total_score - old_total) > 0.001:
            changed += 1
        _update_analytics(db, sub.student_id, exam.school_id, results)
    db.commit()
    return {"affected": len(submissions), "changed": changed}


def _rollback_analytics(db: Session, sub: models.Submission) -> None:
    """Subtract this submission's old contribution from analytics rollups."""
    school_id = sub.exam_id.split(":")[0] if ":" in sub.exam_id else ""
    for r in sub.question_results or []:
        cd = r.get("chuyen_de")
        if not cd:
            continue
        row = db.query(models.Analytics).filter_by(student_id=sub.student_id, chuyen_de=cd, school_id=school_id).first()
        if not row:
            continue
        row.attempts = max(0, (row.attempts or 1) - 1)
        if r.get("is_correct"):
            row.correct = max(0, (row.correct or 1) - 1)
        row.total_score = max(0.0, (row.total_score or 0.0) - float(r.get("score", 0)))
        row.max_score = max(0.0, (row.max_score or 0.0) - float(r.get("max_score", 0)))


def student_history(db: Session, student_id: str, limit: int = 20) -> list[models.Submission]:
    return (
        db.query(models.Submission)
        .filter_by(student_id=student_id)
        .order_by(models.Submission.graded_at.desc())
        .limit(limit)
        .all()
    )


def student_analytics(db: Session, student_id: str) -> list[dict]:
    rows = db.query(models.Analytics).filter_by(student_id=student_id).all()
    out = []
    for r in rows:
        avg = round((r.total_score / r.max_score * 10) if r.max_score else 0.0, 2)
        out.append({
            "chuyen_de": r.chuyen_de,
            "school_id": r.school_id,
            "attempts": r.attempts,
            "correct": r.correct,
            "accuracy": round(r.correct / r.attempts, 2) if r.attempts else 0.0,
            "average_score_10": avg,
        })
    return sorted(out, key=lambda x: x["average_score_10"], reverse=True)


def rankings_for_school(db: Session, school_id: str, period: str = "total", limit: int = 50) -> list[dict]:
    """Compute rankings for a school in a given period: 'total' only for MVP."""
    q = (
        db.query(models.Submission, models.User)
        .join(models.User, models.Submission.student_id == models.User.id)
        .join(models.Exam, models.Submission.exam_id == models.Exam.id)
        .filter(models.Exam.school_id == school_id)
        .filter(models.Submission.counts_for_ranking.is_(True))
    )
    totals: dict[str, dict] = {}
    for sub, user in q:
        key = user.id
        entry = totals.setdefault(key, {"student_id": key, "full_name": user.child_name or user.full_name, "total": 0.0})
        entry["total"] += sub.total_score
    ranked = sorted(totals.values(), key=lambda x: x["total"], reverse=True)[:limit]
    for i, e in enumerate(ranked, 1):
        e["rank"] = i
    return ranked
