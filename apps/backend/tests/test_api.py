"""End-to-end API tests via TestClient."""


def _auth(tok): return {"Authorization": f"Bearer {tok}"}


def _login_admin(client):
    r = client.post("/api/auth/login", json={"email": "admin@demo.vn", "password": "demo1234"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _login_hs(client):
    r = client.post("/api/auth/login", json={"email": "hs@demo.vn", "password": "demo1234"})
    assert r.status_code == 200
    return r.json()["access_token"]


class TestHealth:
    def test_ok(self, client):
        assert client.get("/health").json()["status"] == "ok"


class TestAuth:
    def test_register_pending(self, client):
        r = client.post("/api/auth/register", json={
            "email": "new@x.vn", "password": "pass1234", "full_name": "PH", "child_name": "Con",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "pending_verify"

    def test_pending_cannot_login(self, client):
        client.post("/api/auth/register", json={
            "email": "p1@x.vn", "password": "pass1234", "full_name": "PH", "child_name": "Con",
        })
        r = client.post("/api/auth/login", json={"email": "p1@x.vn", "password": "pass1234"})
        assert r.status_code == 403

    def test_verify_then_login(self, client):
        from app import models
        from app.db import get_session_factory
        client.post("/api/auth/register", json={
            "email": "v1@x.vn", "password": "pass1234", "full_name": "PH", "child_name": "Con",
        })
        # pull token from DB (mock email backend doesn't return token)
        with get_session_factory()() as db:
            user = db.query(models.User).filter_by(email="v1@x.vn").first()
            tok = db.query(models.VerifyToken).filter_by(user_id=user.id, kind="verify_email").first().token
        r = client.get(f"/api/auth/verify/{tok}")
        assert r.status_code == 200
        login = client.post("/api/auth/login", json={"email": "v1@x.vn", "password": "pass1234"})
        assert login.status_code == 200

    def test_dup_register_fails(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@x.vn", "password": "pass1234", "full_name": "PH", "child_name": "Con",
        })
        r = client.post("/api/auth/register", json={
            "email": "dup@x.vn", "password": "pass1234", "full_name": "PH", "child_name": "Con",
        })
        assert r.status_code == 400

    def test_bad_login(self, client):
        assert client.post("/api/auth/login", json={"email": "none@x.vn", "password": "x"}).status_code == 401

    def test_me_requires_auth(self, client):
        assert client.get("/api/auth/me").status_code == 401

    def test_me_ok(self, client):
        tok = _login_hs(client)
        r = client.get("/api/auth/me", headers=_auth(tok))
        assert r.status_code == 200
        assert r.json()["email"] == "hs@demo.vn"

    def test_forgot_password(self, client):
        r = client.post("/api/auth/forgot-password", json={"email": "hs@demo.vn"})
        assert r.status_code == 200

    def test_delete_me(self, client):
        tok = _login_hs(client)
        r = client.delete("/api/me", headers=_auth(tok))
        assert r.status_code == 200


class TestExams:
    def test_schools_listed(self, client):
        assert any(s["id"] == "cau_giay" for s in client.get("/api/schools").json())

    def test_exams_today_auto_gen(self, client):
        tok = _login_hs(client)
        r = client.get("/api/exams/today", headers=_auth(tok))
        assert r.status_code == 200
        assert any(e["school_id"] == "cau_giay" for e in r.json())

    def test_get_exam_detail(self, client):
        tok = _login_hs(client)
        exams = client.get("/api/exams/today", headers=_auth(tok)).json()
        exam_id = exams[0]["exam_id"]
        r = client.get(f"/api/exams/{exam_id}", headers=_auth(tok))
        assert r.status_code == 200 and r.json()["questions"]

    def test_get_missing_exam(self, client):
        tok = _login_hs(client)
        assert client.get("/api/exams/missing", headers=_auth(tok)).status_code == 404


class TestSubmitFlow:
    def test_submit_and_history(self, client):
        tok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(tok)).json()[0]
        payload = {"answers": {"q1": "A"}}
        r = client.post(f"/api/exams/{exam['exam_id']}/submit", json=payload, headers=_auth(tok))
        assert r.status_code == 200
        hist = client.get("/api/me/submissions", headers=_auth(tok))
        assert hist.status_code == 200 and len(hist.json()) == 1
        detail = client.get(f"/api/me/submissions/{r.json()['id']}", headers=_auth(tok))
        assert detail.status_code == 200 and detail.json()["answer_key"]

    def test_submit_missing_exam(self, client):
        tok = _login_hs(client)
        r = client.post("/api/exams/nope/submit", json={"answers": {}}, headers=_auth(tok))
        assert r.status_code == 404

    def test_analytics(self, client):
        tok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(tok)).json()[0]
        client.post(f"/api/exams/{exam['exam_id']}/submit", json={"answers": {"q1": "A"}}, headers=_auth(tok))
        r = client.get("/api/me/analytics", headers=_auth(tok))
        assert r.status_code == 200

    def test_rankings(self, client):
        tok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(tok)).json()[0]
        client.post(f"/api/exams/{exam['exam_id']}/submit", json={"answers": {"q1": "A"}}, headers=_auth(tok))
        r = client.get("/api/rankings/cau_giay", headers=_auth(tok))
        assert r.status_code == 200

    def test_autosave(self, client):
        tok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(tok)).json()[0]
        r = client.post(f"/api/exams/{exam['exam_id']}/autosave", json={"answers": {"q1": "A"}}, headers=_auth(tok))
        assert r.status_code == 200


class TestAppealAPI:
    def test_appeal_and_my_appeals(self, client):
        tok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(tok)).json()[0]
        sub = client.post(f"/api/exams/{exam['exam_id']}/submit", json={"answers": {"q1": "WRONG"}}, headers=_auth(tok)).json()
        r = client.post("/api/appeals", json={"submission_id": sub["id"], "question_id": "q1", "reason": "Em nghĩ đúng"}, headers=_auth(tok))
        assert r.status_code == 200
        mine = client.get("/api/me/appeals", headers=_auth(tok))
        assert mine.status_code == 200 and len(mine.json()) == 1

    def test_appeal_missing_sub(self, client):
        tok = _login_hs(client)
        r = client.post("/api/appeals", json={"submission_id": "x", "question_id": "q1", "reason": "ly do"}, headers=_auth(tok))
        assert r.status_code == 400


class TestAdminAPI:
    def test_admin_stats(self, client):
        atok = _login_admin(client)
        r = client.get("/api/admin/stats", headers=_auth(atok))
        assert r.status_code == 200

    def test_admin_appeals_queue(self, client):
        htok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(htok)).json()[0]
        sub = client.post(f"/api/exams/{exam['exam_id']}/submit", json={"answers": {"q1": "W"}}, headers=_auth(htok)).json()
        client.post("/api/appeals", json={"submission_id": sub["id"], "question_id": "q1", "reason": "ly do"}, headers=_auth(htok))
        atok = _login_admin(client)
        r = client.get("/api/admin/appeals", headers=_auth(atok))
        assert r.status_code == 200 and len(r.json()) == 1

    def test_admin_resolve_accept(self, client):
        htok = _login_hs(client)
        exam = client.get("/api/exams/today", headers=_auth(htok)).json()[0]
        sub = client.post(f"/api/exams/{exam['exam_id']}/submit", json={"answers": {"q1": "W"}}, headers=_auth(htok)).json()
        ap = client.post("/api/appeals", json={"submission_id": sub["id"], "question_id": "q1", "reason": "ly do"}, headers=_auth(htok)).json()
        atok = _login_admin(client)
        r = client.post(f"/api/admin/appeals/{ap['appeal_id']}/resolve",
                        json={"action": "accept", "admin_note": "ok", "new_correct": "W"},
                        headers=_auth(atok))
        assert r.status_code == 200 and r.json()["status"] == "accepted"

    def test_admin_resolve_missing(self, client):
        atok = _login_admin(client)
        r = client.post("/api/admin/appeals/missing/resolve", json={"action": "accept"}, headers=_auth(atok))
        assert r.status_code == 400

    def test_admin_blueprint_upload(self, client):
        atok = _login_admin(client)
        r = client.post("/api/admin/blueprints", json={
            "school_id": "cau_giay",
            "structure": {"total_questions": 8, "question_type_distribution": {"multiple_choice": 8}},
        }, headers=_auth(atok))
        assert r.status_code == 200 and r.json()["version"] == 2

    def test_admin_regenerate(self, client):
        atok = _login_admin(client)
        r = client.post("/api/admin/exams/cau_giay/regenerate", headers=_auth(atok))
        assert r.status_code == 200

    def test_non_admin_blocked(self, client):
        htok = _login_hs(client)
        r = client.get("/api/admin/stats", headers=_auth(htok))
        assert r.status_code == 403
