"""Tests for llm_grader (mock paths)."""

import pytest

from app.llm_grader import EssayGrade, _extract_json, grade_essay, mock_grade


REFERENCE = {
    "correct": "27",
    "narrative": "Tổng ba số = 25 × 3 = 75. Số thứ ba = 75 - 20 - 28 = 27.",
    "steps": [
        {"desc": "Tính tổng", "formula": "25 × 3 = 75", "points": 0.4},
        {"desc": "Tính số thứ ba", "formula": "75 - 20 - 28 = 27", "points": 0.6},
    ],
}


def test_mock_grade_empty_answer() -> None:
    grade = mock_grade("", REFERENCE, max_score=1.0)
    assert grade.score == 0.0
    assert grade.confidence == 1.0


def test_mock_grade_correct_answer_boosts_score() -> None:
    grade = mock_grade("Tổng ba số là 75, vậy số thứ ba là 27", REFERENCE, max_score=1.0)
    assert grade.score > 0.5
    assert grade.confidence >= 0.5


def test_mock_grade_partial_overlap() -> None:
    grade = mock_grade("Tổng ba số bằng 100", REFERENCE, max_score=1.0)
    assert 0 <= grade.score <= 1.0


def test_mock_grade_no_steps() -> None:
    grade = mock_grade("Đáp số 27", {"correct": "27", "steps": [], "narrative": ""}, max_score=1.0)
    assert grade.score > 0


def test_grade_essay_uses_mock_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
    grade = grade_essay("Kết quả 27", REFERENCE, "Tính...", 1.0)
    assert isinstance(grade, EssayGrade)


def test_extract_json_finds_object() -> None:
    assert _extract_json("Here is {\"a\": 1} the result") == '{"a": 1}'


def test_extract_json_missing_raises() -> None:
    with pytest.raises(ValueError):
        _extract_json("no json here")


def test_llm_grade_falls_back_when_no_key(monkeypatch) -> None:
    from app.llm_grader import llm_grade
    monkeypatch.setenv("DAILYEXAM_ANTHROPIC_API_KEY", "")
    grade = llm_grade("ans", REFERENCE, "q", 1.0)
    assert isinstance(grade, EssayGrade)
