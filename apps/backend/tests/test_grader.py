"""Grader tests."""

from app.grader import (
    grade_essay_llm,
    grade_essay_mock,
    grade_multiple_choice,
    grade_numeric,
    grade_question,
)


REF = {
    "correct": "27",
    "narrative": "Tổng = 75, kết quả = 27",
    "steps": [
        {"desc": "Tổng", "formula": "25 × 3 = 75", "points": 0.4},
        {"desc": "Kết quả", "formula": "75 - 20 - 28 = 27", "points": 0.6},
    ],
}


class TestMCQ:
    def test_correct(self):
        r = grade_multiple_choice("q1", "C", "C", 1.0)
        assert r.is_correct and r.score == 1.0

    def test_case_insensitive(self):
        assert grade_multiple_choice("q1", "c", "C", 1.0).is_correct

    def test_wrong(self):
        r = grade_multiple_choice("q1", "A", "C", 1.0)
        assert not r.is_correct and r.score == 0
        assert r.feedback is not None

    def test_empty(self):
        assert not grade_multiple_choice("q1", "", "C", 1.0).is_correct


class TestNumeric:
    def test_correct(self):
        assert grade_numeric("q1", "27", "27", 1.0).is_correct

    def test_fraction_decimal(self):
        assert grade_numeric("q1", "1/2", "0.5", 1.0).is_correct

    def test_wrong(self):
        r = grade_numeric("q1", "28", "27", 1.0)
        assert not r.is_correct and r.score == 0


class TestEssayMock:
    def test_empty(self):
        r = grade_essay_mock("q1", "", REF, 2.0)
        assert r.score == 0 and not r.is_correct

    def test_has_answer(self):
        r = grade_essay_mock("q1", "Tổng 75, số thứ ba 27", REF, 2.0)
        assert r.score > 0 and r.confidence >= 0.5

    def test_partial(self):
        r = grade_essay_mock("q1", "random text", REF, 2.0)
        assert 0 <= r.score <= 2.0

    def test_no_steps(self):
        r = grade_essay_mock("q1", "27", {"correct": "27", "narrative": "", "steps": []}, 1.0)
        assert r.score > 0


class TestLLM:
    def test_fallback_when_mock(self, monkeypatch):
        monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
        r = grade_essay_llm("q1", "27", REF, "?", 1.0)
        assert r.score >= 0


class TestDispatch:
    def _q(self, qid, qtype, **kw):
        return {"id": qid, "type": qtype, "max_score": kw.get("max_score", 1.0),
                "content": kw.get("content", "x")}

    def test_mcq(self):
        assert grade_question(self._q("q1", "multiple_choice"), "C", {"correct": "C"}).is_correct

    def test_numeric(self):
        assert grade_question(self._q("q2", "numeric"), "27", {"correct": "27"}).is_correct

    def test_essay(self):
        r = grade_question(self._q("q3", "essay", max_score=2.0), "27", REF)
        assert r.score >= 0

    def test_disabled_skipped(self):
        r = grade_question(self._q("q4", "multiple_choice"), "A", {"correct": "C", "disabled": True})
        assert r.is_correct and r.score == 0 and r.max_score == 0

    def test_unknown_type_raises(self):
        import pytest
        with pytest.raises(ValueError):
            grade_question(self._q("q5", "mystery"), "A", {"correct": "A"})
