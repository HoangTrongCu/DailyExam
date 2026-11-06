"""Tests for the grader."""

import pytest

from app.grader import (
    grade_essay_stub,
    grade_multiple_choice,
    grade_numeric,
    grade_question,
)
from app.schemas import DifficultyLevel, Question, QuestionType


def _mcq(max_score: float = 1.0) -> Question:
    return Question(
        id="q1",
        index=1,
        type=QuestionType.MULTIPLE_CHOICE,
        difficulty=DifficultyLevel.TH,
        chuyen_de="ti_so_phan_tram",
        content="x",
        max_score=max_score,
        choices=["A", "B", "C", "D"],
    )


def _numeric(max_score: float = 1.0) -> Question:
    return Question(
        id="q2",
        index=2,
        type=QuestionType.NUMERIC,
        difficulty=DifficultyLevel.TH,
        chuyen_de="trung_binh_cong",
        content="x",
        max_score=max_score,
    )


def _essay(max_score: float = 2.0) -> Question:
    return Question(
        id="q3",
        index=3,
        type=QuestionType.ESSAY,
        difficulty=DifficultyLevel.VD,
        chuyen_de="trung_binh_cong",
        content="x",
        max_score=max_score,
    )


class TestGradeMultipleChoice:
    def test_correct(self) -> None:
        result = grade_multiple_choice(_mcq(), "C", "C")
        assert result.is_correct
        assert result.score == 1.0
        assert result.confidence == 1.0

    def test_wrong(self) -> None:
        result = grade_multiple_choice(_mcq(), "A", "C")
        assert not result.is_correct
        assert result.score == 0.0
        assert result.feedback is not None

    def test_case_insensitive(self) -> None:
        assert grade_multiple_choice(_mcq(), "c", "C").is_correct

    def test_whitespace(self) -> None:
        assert grade_multiple_choice(_mcq(), " C ", "C").is_correct

    def test_empty(self) -> None:
        assert not grade_multiple_choice(_mcq(), "", "C").is_correct


class TestGradeNumeric:
    def test_correct(self) -> None:
        result = grade_numeric(_numeric(), "27", "27")
        assert result.is_correct
        assert result.score == 1.0

    def test_equivalent_forms(self) -> None:
        assert grade_numeric(_numeric(), "1/2", "0.5").is_correct
        assert grade_numeric(_numeric(), "50%", "0.5").is_correct

    def test_wrong(self) -> None:
        result = grade_numeric(_numeric(), "28", "27")
        assert not result.is_correct
        assert result.score == 0.0

    def test_invalid_input(self) -> None:
        result = grade_numeric(_numeric(), "abc", "27")
        assert not result.is_correct


class TestGradeEssayStub:
    def test_empty_gets_zero(self) -> None:
        r = grade_essay_stub(_essay(), "", "foo bar baz")
        assert r.score == 0.0
        assert not r.is_correct

    def test_full_overlap(self) -> None:
        r = grade_essay_stub(_essay(), "foo bar baz", "foo bar baz")
        assert r.score == 2.0
        assert r.is_correct

    def test_partial_overlap(self) -> None:
        r = grade_essay_stub(_essay(), "foo other", "foo bar baz")
        assert 0 < r.score < 2.0
        assert not r.is_correct

    def test_empty_outline(self) -> None:
        r = grade_essay_stub(_essay(), "something written", "")
        assert r.score == 0.0


class TestGradeQuestionDispatch:
    def test_mcq_dispatched(self) -> None:
        result = grade_question(_mcq(), "C", "C")
        assert result.is_correct

    def test_numeric_dispatched(self) -> None:
        result = grade_question(_numeric(), "27", "27")
        assert result.is_correct

    def test_essay_dispatched(self) -> None:
        result = grade_question(_essay(), "foo bar baz", "foo bar baz")
        assert result.is_correct

    def test_unknown_type_raises(self) -> None:
        q = _mcq()
        q.type = "unknown"  # type: ignore[assignment]
        with pytest.raises(ValueError):
            grade_question(q, "A", "A")
