"""End-to-end API tests."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
    monkeypatch.setenv("DAILYEXAM_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
    import app.db as db_module
    db_module._engine = None
    db_module._SessionLocal = None

    app = create_app()
    with TestClient(app) as c:
        yield c


def _register(client, email: str, role: str = "student"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": "pass1234", "full_name": "X", "role": role, "school_id": "cau_giay"},
    )
    assert resp.status_code == 200
    return resp.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestHealth:
    def test_health(self, client) -> None:
        assert client.get("/health").json()["status"] == "ok"


class TestAuth:
    def test_register_login_me(self, client) -> None:
        reg = _register(client, "x@y.vn")
        assert reg["access_token"]
        login = client.post("/api/auth/login", json={"email": "x@y.vn", "password": "pass1234"})
        assert login.status_code == 200
        me = client.get("/api/auth/me", headers=_auth(login.json()["access_token"]))
        assert me.json()["email"] == "x@y.vn"

    def test_duplicate_register_fails(self, client) -> None:
        _register(client, "dup@y.vn")
        resp = client.post(
            "/api/auth/register",
            json={"email": "dup@y.vn", "password": "pass1234", "full_name": "X", "role": "student"},
        )
        assert resp.status_code == 400

    def test_invalid_login(self, client) -> None:
        _register(client, "a@y.vn")
        resp = client.post("/api/auth/login", json={"email": "a@y.vn", "password": "wrong"})
        assert resp.status_code == 401

    def test_me_without_token(self, client) -> None:
        assert client.get("/api/auth/me").status_code == 401


class TestSchools:
    def test_seeded_school_listed(self, client) -> None:
        assert any(s["id"] == "cau_giay" for s in client.get("/api/schools").json())

    def test_get_school_detail(self, client) -> None:
        assert client.get("/api/schools/cau_giay").status_code == 200

    def test_missing_school_404(self, client) -> None:
        assert client.get("/api/schools/unknown").status_code == 404


class TestExams:
    def test_get_auto_generates_exam(self, client) -> None:
        resp = client.get("/api/schools/cau_giay/exams/2026-11-07")
        assert resp.status_code == 200
        exam = resp.json()
        assert exam["school_id"] == "cau_giay"
        assert len(exam["questions"]) == 10

    def test_teacher_can_regenerate(self, client) -> None:
        teacher = _register(client, "teacher@y.vn", role="teacher")
        resp = client.post(
            "/api/schools/cau_giay/exams/2026-11-08/generate",
            headers=_auth(teacher["access_token"]),
        )
        assert resp.status_code == 200

    def test_student_cannot_force_regenerate(self, client) -> None:
        student = _register(client, "s@y.vn")
        resp = client.post(
            "/api/schools/cau_giay/exams/2026-11-09/generate",
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 403


class TestSubmissions:
    def test_submit_full_cycle(self, client) -> None:
        student = _register(client, "hs@y.vn")
        exam = client.get("/api/schools/cau_giay/exams/2026-11-07").json()
        answers = {}
        # Fill a couple correct answers (use the auto-generated correct via view)
        # We can only submit arbitrary answers here (public view excludes answers)
        for q in exam["questions"][:3]:
            if q["type"] == "multiple_choice":
                answers[q["id"]] = "A"
            else:
                answers[q["id"]] = "0"
        resp = client.post(
            "/api/submissions",
            json={"exam_id": exam["id"], "answers": answers},
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "total_score" in body
        assert "question_results" in body

    def test_submit_requires_auth(self, client) -> None:
        resp = client.post("/api/submissions", json={"exam_id": "x:1", "answers": {}})
        assert resp.status_code == 401

    def test_invalid_exam_id(self, client) -> None:
        student = _register(client, "hs2@y.vn")
        resp = client.post(
            "/api/submissions",
            json={"exam_id": "badformat", "answers": {}},
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 400

    def test_invalid_date(self, client) -> None:
        student = _register(client, "hs3@y.vn")
        resp = client.post(
            "/api/submissions",
            json={"exam_id": "cau_giay:bad-date", "answers": {}},
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 400

    def test_my_submissions_and_analytics(self, client) -> None:
        student = _register(client, "hs4@y.vn")
        exam = client.get("/api/schools/cau_giay/exams/2026-11-07").json()
        client.post(
            "/api/submissions",
            json={"exam_id": exam["id"], "answers": {exam["questions"][0]["id"]: "A"}},
            headers=_auth(student["access_token"]),
        )
        subs = client.get("/api/me/submissions", headers=_auth(student["access_token"]))
        assert subs.status_code == 200
        assert len(subs.json()) == 1
        ana = client.get("/api/me/analytics", headers=_auth(student["access_token"]))
        assert ana.status_code == 200


class TestTeacher:
    def test_teacher_sees_submissions(self, client) -> None:
        student = _register(client, "hs5@y.vn")
        exam = client.get("/api/schools/cau_giay/exams/2026-11-07").json()
        client.post(
            "/api/submissions",
            json={"exam_id": exam["id"], "answers": {exam["questions"][0]["id"]: "A"}},
            headers=_auth(student["access_token"]),
        )
        teacher = _register(client, "t2@y.vn", role="teacher")
        resp = client.get("/api/teacher/submissions", headers=_auth(teacher["access_token"]))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_student_cannot_see_teacher_endpoint(self, client) -> None:
        student = _register(client, "hs6@y.vn")
        resp = client.get("/api/teacher/submissions", headers=_auth(student["access_token"]))
        assert resp.status_code == 403
