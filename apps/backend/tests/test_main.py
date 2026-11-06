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


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _admin_token(client):
    """Login as seeded admin to get a token."""
    resp = client.post("/api/auth/login", json={"email": "admin@demo.vn", "password": "demo1234"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _register_and_approve(client, email: str, role: str = "student"):
    """Register a pending user, then approve via admin, then return the login token."""
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "pass1234", "full_name": email, "school_id": "cau_giay"},
    )
    assert reg.status_code == 200, reg.text
    user_id = reg.json()["user_id"]
    # Approve
    admin_token = _admin_token(client)
    approve = client.post(f"/api/admin/users/{user_id}/approve", headers=_auth(admin_token))
    assert approve.status_code == 200
    # Optionally promote role (seeded admin only; we just change via DB in tests when needed)
    # Login as the new user
    login = client.post("/api/auth/login", json={"email": email, "password": "pass1234"})
    assert login.status_code == 200, login.text
    return login.json()


class TestHealth:
    def test_health(self, client) -> None:
        assert client.get("/health").json()["status"] == "ok"


class TestAuth:
    def test_register_returns_pending(self, client) -> None:
        resp = client.post(
            "/api/auth/register",
            json={"email": "new@y.vn", "password": "pass1234", "full_name": "New"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "pending"
        assert "access_token" not in body

    def test_pending_cannot_login(self, client) -> None:
        client.post(
            "/api/auth/register",
            json={"email": "pending@y.vn", "password": "pass1234", "full_name": "P"},
        )
        resp = client.post("/api/auth/login", json={"email": "pending@y.vn", "password": "pass1234"})
        assert resp.status_code == 403
        assert "phê duyệt" in resp.json()["detail"]

    def test_register_login_me_after_approval(self, client) -> None:
        tok = _register_and_approve(client, "x@y.vn")
        assert tok["access_token"]
        me = client.get("/api/auth/me", headers=_auth(tok["access_token"]))
        assert me.json()["email"] == "x@y.vn"

    def test_duplicate_register_fails(self, client) -> None:
        client.post("/api/auth/register", json={"email": "dup@y.vn", "password": "pass1234", "full_name": "X"})
        resp = client.post(
            "/api/auth/register",
            json={"email": "dup@y.vn", "password": "pass1234", "full_name": "X"},
        )
        assert resp.status_code == 400

    def test_invalid_login(self, client) -> None:
        _register_and_approve(client, "a@y.vn")
        resp = client.post("/api/auth/login", json={"email": "a@y.vn", "password": "wrong"})
        assert resp.status_code == 401

    def test_me_without_token(self, client) -> None:
        assert client.get("/api/auth/me").status_code == 401


class TestAdminApproval:
    def test_admin_lists_pending(self, client) -> None:
        client.post("/api/auth/register", json={"email": "p1@y.vn", "password": "pass1234", "full_name": "P1"})
        client.post("/api/auth/register", json={"email": "p2@y.vn", "password": "pass1234", "full_name": "P2"})
        tok = _admin_token(client)
        resp = client.get("/api/admin/users?status=pending", headers=_auth(tok))
        assert resp.status_code == 200
        pending = resp.json()
        assert len(pending) >= 2
        assert all(u["status"] == "pending" for u in pending)

    def test_non_admin_cannot_list(self, client) -> None:
        tok = _register_and_approve(client, "notadmin@y.vn")
        resp = client.get("/api/admin/users?status=pending", headers=_auth(tok["access_token"]))
        assert resp.status_code == 403

    def test_approve_allows_login(self, client) -> None:
        reg = client.post(
            "/api/auth/register",
            json={"email": "ap@y.vn", "password": "pass1234", "full_name": "A"},
        ).json()
        tok = _admin_token(client)
        client.post(f"/api/admin/users/{reg['user_id']}/approve", headers=_auth(tok))
        login = client.post("/api/auth/login", json={"email": "ap@y.vn", "password": "pass1234"})
        assert login.status_code == 200

    def test_reject_blocks_login(self, client) -> None:
        reg = client.post(
            "/api/auth/register",
            json={"email": "rj@y.vn", "password": "pass1234", "full_name": "R"},
        ).json()
        tok = _admin_token(client)
        client.post(f"/api/admin/users/{reg['user_id']}/reject", headers=_auth(tok))
        login = client.post("/api/auth/login", json={"email": "rj@y.vn", "password": "pass1234"})
        assert login.status_code == 403

    def test_approve_missing_user(self, client) -> None:
        tok = _admin_token(client)
        resp = client.post("/api/admin/users/no-such-id/approve", headers=_auth(tok))
        assert resp.status_code == 404

    def test_reject_missing_user(self, client) -> None:
        tok = _admin_token(client)
        resp = client.post("/api/admin/users/no-such-id/reject", headers=_auth(tok))
        assert resp.status_code == 404


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

    def test_admin_can_regenerate(self, client) -> None:
        tok = _admin_token(client)
        resp = client.post(
            "/api/schools/cau_giay/exams/2026-11-08/generate",
            headers=_auth(tok),
        )
        assert resp.status_code == 200

    def test_student_cannot_force_regenerate(self, client) -> None:
        student = _register_and_approve(client, "s@y.vn")
        resp = client.post(
            "/api/schools/cau_giay/exams/2026-11-09/generate",
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 403


class TestSubmissions:
    def test_submit_full_cycle(self, client) -> None:
        student = _register_and_approve(client, "hs@y.vn")
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
        student = _register_and_approve(client, "hs2@y.vn")
        resp = client.post(
            "/api/submissions",
            json={"exam_id": "badformat", "answers": {}},
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 400

    def test_invalid_date(self, client) -> None:
        student = _register_and_approve(client, "hs3@y.vn")
        resp = client.post(
            "/api/submissions",
            json={"exam_id": "cau_giay:bad-date", "answers": {}},
            headers=_auth(student["access_token"]),
        )
        assert resp.status_code == 400

    def test_my_submissions_and_analytics(self, client) -> None:
        student = _register_and_approve(client, "hs4@y.vn")
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


