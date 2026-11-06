"""Tests for the data store."""

from datetime import date

from app.schemas import ExamStatus
from app.store import correct_answer_for, get_daily_exam, get_school, list_schools


class TestSchools:
    def test_list_contains_cau_giay(self) -> None:
        schools = list_schools()
        assert any(s.id == "cau_giay" for s in schools)

    def test_get_existing_school(self) -> None:
        school = get_school("cau_giay")
        assert school is not None
        assert "Cầu Giấy" in school.name

    def test_get_missing_school(self) -> None:
        assert get_school("nonexistent") is None


class TestDailyExam:
    def test_sample_exam_shape(self) -> None:
        exam = get_daily_exam("cau_giay", date(2026, 11, 6))
        assert exam is not None
        assert exam.status == ExamStatus.READY
        assert len(exam.questions) == 3
        assert exam.total_score > 0

    def test_exam_for_unknown_school(self) -> None:
        assert get_daily_exam("unknown", date(2026, 11, 6)) is None

    def test_exam_id_format(self) -> None:
        exam = get_daily_exam("cau_giay", date(2026, 11, 6))
        assert exam is not None
        assert exam.id == "cau_giay:2026-11-06"


class TestCorrectAnswers:
    def test_known(self) -> None:
        assert correct_answer_for("q1") == "C"
        assert correct_answer_for("q2") == "27"

    def test_unknown(self) -> None:
        assert correct_answer_for("missing") == ""
