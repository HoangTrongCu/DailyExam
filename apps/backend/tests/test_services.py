"""Integration tests covering services + composer + submission flow."""

from datetime import date

import pytest

from app import models
from app.config import Settings
from app.exam_composer import compose_exam
from app.services import exam_service, submission_service, user_service


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Isolated SQLite DB per test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DAILYEXAM_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
    import app.db as db_module
    db_module._engine = None
    db_module._SessionLocal = None
    from app.db import get_session_factory, init_db
    init_db()
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def _seed_school(db) -> None:
    db.add(
        models.School(
            id="cau_giay",
            name="THCS Cầu Giấy",
            short_name="Cầu Giấy",
            grade_levels=["lop_5"],
            config={"num_questions": 5, "duration_minutes": 45},
        )
    )
    db.commit()


# ─── compose_exam ─────────────────────────────────────────
class TestCompose:
    def test_basic_composition(self) -> None:
        exam_service.ensure_templates_loaded()
        comp = compose_exam("cau_giay", date(2026, 11, 7), num_questions=5, seed=1)
        assert len(comp.questions) == 5
        assert comp.answer_key
        assert comp.gate_open_at < comp.gate_close_at

    def test_difficulty_distribution_respected(self) -> None:
        exam_service.ensure_templates_loaded()
        comp = compose_exam(
            "cau_giay",
            date(2026, 11, 7),
            num_questions=10,
            config={"difficulty_distribution": {"NB": 0.5, "TH": 0.5, "VD": 0.0, "VDC": 0.0}},
            seed=2,
        )
        difficulties = [q["difficulty"] for q in comp.questions]
        easy_count = sum(1 for d in difficulties if d in ["NB", "TH"])
        assert easy_count >= 8


# ─── exam_service ─────────────────────────────────────────
class TestExamService:
    def test_generate_and_fetch(self, db) -> None:
        _seed_school(db)
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        assert exam.id
        # Idempotent
        again = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        assert again.id == exam.id

    def test_generate_unknown_school_raises(self, db) -> None:
        with pytest.raises(ValueError):
            exam_service.generate_daily_exam(db, "nope", date(2026, 11, 7))

    def test_public_view_strips_answers(self, db) -> None:
        _seed_school(db)
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        view = exam_service.public_view(exam)
        assert "answer_key" not in view

    def test_get_nonexistent(self, db) -> None:
        _seed_school(db)
        assert exam_service.get_daily_exam(db, "cau_giay", date(1999, 1, 1)) is None


# ─── user_service ─────────────────────────────────────────
class TestUserService:
    def test_create_and_authenticate(self, db) -> None:
        user = user_service.create_user(db, "a@b.c", "pass1234", "A")
        assert user_service.authenticate(db, "a@b.c", "pass1234").id == user.id

    def test_duplicate_email_raises(self, db) -> None:
        user_service.create_user(db, "a@b.c", "pass1234", "A")
        with pytest.raises(ValueError):
            user_service.create_user(db, "a@b.c", "pass5678", "A2")

    def test_authenticate_bad_password(self, db) -> None:
        user_service.create_user(db, "a@b.c", "pass1234", "A")
        assert user_service.authenticate(db, "a@b.c", "wrong") is None

    def test_authenticate_missing_user(self, db) -> None:
        assert user_service.authenticate(db, "none@x.y", "p") is None


# ─── submission_service end-to-end ────────────────────────
class TestSubmissionService:
    def test_submit_grades_and_persists(self, db) -> None:
        _seed_school(db)
        student = user_service.create_user(
            db, "hs@x.vn", "p1234567", "Nam", role="student", school_id="cau_giay"
        )
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first_q = exam.exam_data["questions"][0]
        answers = {first_q["id"]: exam.answer_key[first_q["id"]]["correct"]}
        sub = submission_service.submit_and_grade(db, exam, student, answers)
        assert sub.total_score > 0
        assert sub.max_total_score > 0

    def test_submit_is_idempotent(self, db) -> None:
        _seed_school(db)
        student = user_service.create_user(db, "hs2@x.vn", "p1234567", "Hà", school_id="cau_giay")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = submission_service.submit_and_grade(db, exam, student, {})
        second = submission_service.submit_and_grade(db, exam, student, {})
        assert first.id == second.id

    def test_history_and_analytics(self, db) -> None:
        _seed_school(db)
        student = user_service.create_user(db, "hs3@x.vn", "p1234567", "An", school_id="cau_giay")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first_q = exam.exam_data["questions"][0]
        submission_service.submit_and_grade(
            db, exam, student, {first_q["id"]: exam.answer_key[first_q["id"]]["correct"]}
        )
        history = submission_service.student_history(db, student.id)
        assert len(history) == 1
        analytics = submission_service.student_analytics(db, student.id)
        assert analytics
        assert all("chuyen_de" in a for a in analytics)
