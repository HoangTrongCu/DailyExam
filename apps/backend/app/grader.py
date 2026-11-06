"""Grading service for MCQ, numeric, and essay questions.

Essay grading is stubbed at this phase and will call an LLM service in Phase 5.
"""

from __future__ import annotations

from app.math_engine import numbers_equal
from app.schemas import Question, QuestionResult, QuestionType


def grade_multiple_choice(question: Question, answer: str, correct: str) -> QuestionResult:
    """Grade an MCQ question by exact match."""
    normalized_student = answer.strip().upper()
    normalized_correct = correct.strip().upper()
    is_correct = normalized_student == normalized_correct and bool(normalized_student)
    return QuestionResult(
        question_id=question.id,
        score=question.max_score if is_correct else 0.0,
        max_score=question.max_score,
        is_correct=is_correct,
        feedback=None if is_correct else f"Đáp án đúng là {correct}",
        confidence=1.0,
    )


def grade_numeric(question: Question, answer: str, correct: str) -> QuestionResult:
    """Grade a fill-in-the-number question using SymPy comparison."""
    is_correct = numbers_equal(answer, correct)
    return QuestionResult(
        question_id=question.id,
        score=question.max_score if is_correct else 0.0,
        max_score=question.max_score,
        is_correct=is_correct,
        feedback=None if is_correct else f"Đáp án đúng là {correct}",
        confidence=0.99,
    )


def grade_essay_stub(question: Question, answer: str, correct_outline: str) -> QuestionResult:
    """Placeholder essay grader — scores by simple keyword overlap.

    Replaced by LLM-based reference grader in Phase 5.
    """
    if not answer.strip():
        return QuestionResult(
            question_id=question.id,
            score=0.0,
            max_score=question.max_score,
            is_correct=False,
            feedback="Chưa có bài làm",
            confidence=1.0,
        )
    tokens_outline = _tokens(correct_outline)
    tokens_student = _tokens(answer)
    if not tokens_outline:
        ratio = 0.0
    else:
        overlap = len(tokens_outline & tokens_student)
        ratio = overlap / len(tokens_outline)
    score = round(question.max_score * ratio, 2)
    return QuestionResult(
        question_id=question.id,
        score=score,
        max_score=question.max_score,
        is_correct=ratio >= 0.9,
        feedback="Chấm tự động theo từ khóa — sẽ được giáo viên review",
        confidence=0.6,
    )


def _tokens(text: str) -> set[str]:
    return {t for t in text.lower().split() if len(t) > 1}


def grade_question(
    question: Question,
    student_answer: str,
    correct_answer: str,
) -> QuestionResult:
    """Dispatch grading by question type."""
    if question.type == QuestionType.MULTIPLE_CHOICE:
        return grade_multiple_choice(question, student_answer, correct_answer)
    if question.type == QuestionType.NUMERIC:
        return grade_numeric(question, student_answer, correct_answer)
    if question.type == QuestionType.ESSAY:
        return grade_essay_stub(question, student_answer, correct_answer)
    raise ValueError(f"Unsupported question type: {question.type}")
