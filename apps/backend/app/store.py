"""In-memory sample data store.

Phase 1 uses hardcoded sample data. Replaced by PostgreSQL repositories in Phase 2.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from app.config import get_settings
from app.schemas import (
    DailyExam,
    DifficultyLevel,
    ExamStatus,
    Question,
    QuestionType,
    School,
)

ICT = timezone(timedelta(hours=7))

SCHOOLS: dict[str, School] = {
    "cau_giay": School(
        id="cau_giay",
        name="THCS Cầu Giấy",
        short_name="Cầu Giấy",
        grade_levels=["lop_5", "lop_6"],
    ),
}

_CORRECT_ANSWERS: dict[str, str] = {
    "q1": "C",
    "q2": "27",
    "q3": "Số thứ ba bằng tổng trừ tổng hai số đã biết",
}


def list_schools() -> list[School]:
    """Return all registered schools."""
    return list(SCHOOLS.values())


def get_school(school_id: str) -> School | None:
    """Return a school by id or None."""
    return SCHOOLS.get(school_id)


def _build_sample_exam(school_id: str, exam_date: date) -> DailyExam:
    settings = get_settings()
    gate_open = datetime.combine(exam_date, time(settings.gate_open_hour, 0), tzinfo=ICT)
    gate_close = datetime.combine(exam_date, time(settings.gate_close_hour, 0), tzinfo=ICT)
    questions = [
        Question(
            id="q1",
            index=1,
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.TH,
            chuyen_de="ti_so_phan_tram",
            content=(
                "Có 1500 du khách được hỏi. 25% thích phở, 18% thích bánh cuốn, "
                "43% thích bún chả, còn lại thích bánh mỳ. Hỏi bao nhiêu người thích bánh mỳ?"
            ),
            max_score=0.75,
            choices=["180", "195", "210", "225"],
        ),
        Question(
            id="q2",
            index=2,
            type=QuestionType.NUMERIC,
            difficulty=DifficultyLevel.TH,
            chuyen_de="trung_binh_cong",
            content=(
                "Trung bình cộng của ba số là 25. Số thứ nhất là 20, số thứ hai là 28. "
                "Tìm số thứ ba."
            ),
            max_score=1.0,
        ),
        Question(
            id="q3",
            index=3,
            type=QuestionType.ESSAY,
            difficulty=DifficultyLevel.VD,
            chuyen_de="trung_binh_cong",
            content="Trình bày cách giải bài toán ở câu 2.",
            max_score=1.5,
        ),
    ]
    total_score = sum(q.max_score for q in questions)
    return DailyExam(
        id=f"{school_id}:{exam_date.isoformat()}",
        school_id=school_id,
        exam_date=exam_date,
        status=ExamStatus.READY,
        total_score=total_score,
        duration_minutes=60,
        questions=questions,
        gate_open_at=gate_open,
        gate_close_at=gate_close,
    )


def get_daily_exam(school_id: str, exam_date: date) -> DailyExam | None:
    """Return the daily exam for a school (sample data)."""
    if school_id not in SCHOOLS:
        return None
    return _build_sample_exam(school_id, exam_date)


def correct_answer_for(question_id: str) -> str:
    """Return the correct answer for a sample question."""
    return _CORRECT_ANSWERS.get(question_id, "")
