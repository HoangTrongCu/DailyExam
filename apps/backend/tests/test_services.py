"""Services layer tests."""

from datetime import date

import pytest

from app import models
from app.services import appeal_service, exam_service, submission_service, user_service


def _seed_school(db):
    db.add(models.School(id="cau_giay", name="THCS Cầu Giấy", short_name="Cầu Giấy"))
    db.commit()


def _active_student(db, email="hs@x.vn"):
    user, _tok = user_service.register_user(db, email, "pass1234", "PH " + email, "Con " + email, status="active")
    return user


class TestUserService:
    def test_register_pending_returns_token(self, db):
        user, tok = user_service.register_user(db, "p@x.vn", "pass1234", "PH", "Con")
        assert user.status == "pending_verify"
        assert tok

    def test_register_duplicate(self, db):
        user_service.register_user(db, "d@x.vn", "pass1234", "PH", "Con")
        with pytest.raises(user_service.AuthError):
            user_service.register_user(db, "d@x.vn", "pass1234", "PH", "Con")

    def test_verify_token_activates(self, db):
        user, tok = user_service.register_user(db, "v@x.vn", "pass1234", "PH", "Con")
        activated = user_service.verify_email_token(db, tok)
        assert activated.status == "active"

    def test_verify_invalid_token(self, db):
        with pytest.raises(user_service.AuthError):
            user_service.verify_email_token(db, "bad")

    def test_verify_used_token(self, db):
        _, tok = user_service.register_user(db, "u1@x.vn", "pass1234", "PH", "Con")
        user_service.verify_email_token(db, tok)
        with pytest.raises(user_service.AuthError):
            user_service.verify_email_token(db, tok)

    def test_pending_cannot_login(self, db):
        user_service.register_user(db, "pp@x.vn", "pass1234", "PH", "Con")
        with pytest.raises(user_service.AuthError) as ex:
            user_service.authenticate_and_rotate_session(db, "pp@x.vn", "pass1234")
        assert ex.value.code == "pending_verify"

    def test_active_login(self, db):
        _active_student(db, "a1@x.vn")
        user, tok = user_service.authenticate_and_rotate_session(db, "a1@x.vn", "pass1234")
        assert tok and user.session_token == tok

    def test_wrong_password(self, db):
        _active_student(db, "a2@x.vn")
        with pytest.raises(user_service.AuthError):
            user_service.authenticate_and_rotate_session(db, "a2@x.vn", "wrong")

    def test_missing_user_login(self, db):
        with pytest.raises(user_service.AuthError):
            user_service.authenticate_and_rotate_session(db, "none@x.vn", "pass1234")

    def test_reset_password_flow(self, db):
        _active_student(db, "r@x.vn")
        tok = user_service.request_password_reset(db, "r@x.vn")
        assert tok
        user_service.reset_password(db, tok, "newpass123")
        user, _ = user_service.authenticate_and_rotate_session(db, "r@x.vn", "newpass123")
        assert user is not None

    def test_reset_unknown_email(self, db):
        assert user_service.request_password_reset(db, "unknown@x.vn") is None

    def test_reset_invalid_token(self, db):
        with pytest.raises(user_service.AuthError):
            user_service.reset_password(db, "bad", "pass1234")

    def test_soft_delete_blocks_login(self, db):
        user = _active_student(db, "del@x.vn")
        user_service.soft_delete(db, user.id)
        with pytest.raises(user_service.AuthError):
            user_service.authenticate_and_rotate_session(db, "del@x.vn", "pass1234")


class TestExamService:
    def test_generate_and_idempotent(self, db):
        _seed_school(db)
        e1 = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        e2 = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        assert e1.id == e2.id

    def test_generate_unknown_school(self, db):
        with pytest.raises(ValueError):
            exam_service.generate_daily_exam(db, "nope", date(2026, 11, 7))

    def test_public_view_strips_answers(self, db):
        _seed_school(db)
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        view = exam_service.public_view(exam)
        assert "answer_key" not in view

    def test_list_for_date(self, db):
        _seed_school(db)
        exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        rows = exam_service.list_exams_for_date(db, date(2026, 11, 7))
        assert len(rows) == 1


class TestSubmission:
    def test_submit_grades(self, db):
        _seed_school(db)
        stu = _active_student(db, "s1@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        sub = submission_service.submit_and_grade(
            db, exam, stu, {first["id"]: exam.answer_key[first["id"]]["correct"]}
        )
        assert sub.total_score > 0

    def test_idempotent(self, db):
        _seed_school(db)
        stu = _active_student(db, "s2@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        a = submission_service.submit_and_grade(db, exam, stu, {})
        b = submission_service.submit_and_grade(db, exam, stu, {})
        assert a.id == b.id

    def test_history_analytics(self, db):
        _seed_school(db)
        stu = _active_student(db, "s3@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        submission_service.submit_and_grade(db, exam, stu, {exam.exam_data["questions"][0]["id"]: "A"})
        assert len(submission_service.student_history(db, stu.id)) == 1
        assert submission_service.student_analytics(db, stu.id)

    def test_rankings(self, db):
        _seed_school(db)
        stu1 = _active_student(db, "r1@x.vn")
        stu2 = _active_student(db, "r2@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        submission_service.submit_and_grade(db, exam, stu1, {first["id"]: exam.answer_key[first["id"]]["correct"]})
        submission_service.submit_and_grade(db, exam, stu2, {})
        ranked = submission_service.rankings_for_school(db, "cau_giay")
        assert ranked and ranked[0]["rank"] == 1


class TestAppeal:
    def test_file_and_resolve_accept(self, db):
        _seed_school(db)
        stu = _active_student(db, "ap1@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        sub = submission_service.submit_and_grade(db, exam, stu, {first["id"]: "WRONG"})
        ap = appeal_service.file_appeal(db, sub.id, stu.id, first["id"], "Tôi nghĩ bài em đúng")
        res = appeal_service.resolve_appeal(db, ap.id, "accept", "Đã chấp nhận",
                                            new_correct="WRONG")  # pretend new answer matches
        assert res["status"] == "accepted"
        assert res["affected"] >= 1

    def test_reject(self, db):
        _seed_school(db)
        stu = _active_student(db, "ap2@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        sub = submission_service.submit_and_grade(db, exam, stu, {})
        ap = appeal_service.file_appeal(db, sub.id, stu.id, first["id"], "Lý do")
        res = appeal_service.resolve_appeal(db, ap.id, "reject", "Nope")
        assert res["status"] == "rejected"

    def test_dedupe(self, db):
        _seed_school(db)
        stu = _active_student(db, "ap3@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        sub = submission_service.submit_and_grade(db, exam, stu, {})
        a1 = appeal_service.file_appeal(db, sub.id, stu.id, first["id"], "Reason")
        a2 = appeal_service.file_appeal(db, sub.id, stu.id, first["id"], "Reason again")
        assert a1.id == a2.id

    def test_missing_submission(self, db):
        with pytest.raises(ValueError):
            appeal_service.file_appeal(db, "no-such", "x", "q1", "r")

    def test_resolve_missing(self, db):
        with pytest.raises(ValueError):
            appeal_service.resolve_appeal(db, "no-id", "accept")

    def test_invalid_action(self, db):
        _seed_school(db)
        stu = _active_student(db, "ap4@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        sub = submission_service.submit_and_grade(db, exam, stu, {})
        ap = appeal_service.file_appeal(db, sub.id, stu.id, first["id"], "r")
        with pytest.raises(ValueError):
            appeal_service.resolve_appeal(db, ap.id, "weird")

    def test_disable_question(self, db):
        _seed_school(db)
        stu = _active_student(db, "dq@x.vn")
        exam = exam_service.generate_daily_exam(db, "cau_giay", date(2026, 11, 7))
        first = exam.exam_data["questions"][0]
        submission_service.submit_and_grade(db, exam, stu, {first["id"]: exam.answer_key[first["id"]]["correct"]})
        res = appeal_service.disable_question(db, exam.id, first["id"])
        assert res["affected"] >= 1
