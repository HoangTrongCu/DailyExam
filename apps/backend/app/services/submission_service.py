"""Submission + grading + analytics service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.grader import grade_multiple_choice, grade_numeric
from app.llm_grader import grade_essay
from app.schemas import Question, QuestionType


def submit_and_grade(
    db: Session,
    exam: models.DailyExamRow,
    student: models.User,
    answers: dict[str, str],
) -> models.Submission:
    """Grade a student's answers and persist a submission. Idempotent per (exam, student)."""
    existing = (
        db.query(models.Submission)
        .filter_by(exam_id=exam.id, student_id=student.id)
        .first()
    )
    if existing:
        return existing

    question_results: list[dict] = []
    total = 0.0
    max_total = 0.0

    for q_dict in exam.exam_data.get("questions", []):
        qid = q_dict["id"]
        question = Question(
            id=qid,
            index=q_dict["index"],
            type=QuestionType(q_dict["type"]),
            difficulty=q_dict["difficulty"],
            chuyen_de=q_dict["chuyen_de"],
            content=q_dict["content"],
            max_score=q_dict["max_score"],
            choices=q_dict.get("choices"),
            unit=q_dict.get("unit"),
        )
        answer = answers.get(qid, "")
        correct_info = exam.answer_key.get(qid, {})
        correct = correct_info.get("correct", "")

        if question.type == QuestionType.MULTIPLE_CHOICE:
            result = grade_multiple_choice(question, answer, correct)
            payload = result.model_dump()
        elif question.type == QuestionType.NUMERIC:
            result = grade_numeric(question, answer, correct)
            payload = result.model_dump()
        else:  # essay
            grade = grade_essay(answer, correct_info, question.content, question.max_score)
            payload = {
                "question_id": qid,
                "score": grade.score,
                "max_score": question.max_score,
                "is_correct": grade.score >= question.max_score * 0.9,
                "feedback": grade.feedback,
                "confidence": grade.confidence,
                "step_scores": grade.step_scores,
            }

        question_results.append({**payload, "chuyen_de": question.chuyen_de})
        total += payload["score"]
        max_total += payload["max_score"]

    percent = round((total / max_total * 100) if max_total else 0.0, 2)

    submission = models.Submission(
        id=str(uuid.uuid4()),
        exam_id=exam.id,
        student_id=student.id,
        answers=answers,
        total_score=round(total, 2),
        max_total_score=round(max_total, 2),
        percentage=percent,
        question_results=question_results,
        graded_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    _update_analytics(db, student.id, question_results)
    db.commit()
    db.refresh(submission)
    return submission


def _update_analytics(db: Session, student_id: str, results: list[dict]) -> None:
    """Roll results into per-chuyen_de stats for the student."""
    for r in results:
        cd = r.get("chuyen_de")
        if not cd:
            continue
        row = (
            db.query(models.Analytics)
            .filter_by(student_id=student_id, chuyen_de=cd)
            .first()
        )
        if not row:
            row = models.Analytics(
                student_id=student_id,
                chuyen_de=cd,
                attempts=0,
                correct=0,
                total_score=0.0,
                max_score=0.0,
            )
            db.add(row)
            db.flush()
        row.attempts = (row.attempts or 0) + 1
        if r.get("is_correct"):
            row.correct = (row.correct or 0) + 1
        row.total_score = (row.total_score or 0.0) + float(r.get("score", 0))
        row.max_score = (row.max_score or 0.0) + float(r.get("max_score", 0))


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
        out.append(
            {
                "chuyen_de": r.chuyen_de,
                "attempts": r.attempts,
                "correct": r.correct,
                "accuracy": round(r.correct / r.attempts, 2) if r.attempts else 0.0,
                "average_score_10": avg,
            }
        )
    return sorted(out, key=lambda x: x["average_score_10"], reverse=True)
