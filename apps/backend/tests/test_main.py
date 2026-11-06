"""Tests for the FastAPI app endpoints."""

from fastapi.testclient import TestClient

from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


class TestHealth:
    def test_health_ok(self) -> None:
        resp = _client().get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["version"]


class TestSchoolsAPI:
    def test_list(self) -> None:
        resp = _client().get("/api/schools")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_existing(self) -> None:
        resp = _client().get("/api/schools/cau_giay")
        assert resp.status_code == 200
        assert resp.json()["id"] == "cau_giay"

    def test_get_missing(self) -> None:
        resp = _client().get("/api/schools/nope")
        assert resp.status_code == 404


class TestExamsAPI:
    def test_get_exam(self) -> None:
        resp = _client().get("/api/schools/cau_giay/exams/2026-11-06")
        assert resp.status_code == 200
        assert resp.json()["school_id"] == "cau_giay"

    def test_get_exam_invalid_school(self) -> None:
        resp = _client().get("/api/schools/nope/exams/2026-11-06")
        assert resp.status_code == 404

    def test_get_exam_invalid_date(self) -> None:
        resp = _client().get("/api/schools/cau_giay/exams/not-a-date")
        assert resp.status_code == 422


class TestSubmissions:
    def _payload(self, answers: list[dict] | None = None) -> dict:
        return {
            "exam_id": "cau_giay:2026-11-06",
            "student_id": "hs_001",
            "answers": answers
            or [
                {"question_id": "q1", "answer": "C"},
                {"question_id": "q2", "answer": "27"},
                {"question_id": "q3", "answer": "Tổng ba số bằng trung bình cộng nhân ba"},
            ],
        }

    def test_submit_success(self) -> None:
        resp = _client().post("/api/submissions", json=self._payload())
        assert resp.status_code == 200
        body = resp.json()
        assert body["student_id"] == "hs_001"
        assert body["total_score"] > 0
        assert len(body["question_results"]) == 3

    def test_submit_all_wrong(self) -> None:
        resp = _client().post(
            "/api/submissions",
            json=self._payload(
                [
                    {"question_id": "q1", "answer": "A"},
                    {"question_id": "q2", "answer": "99"},
                    {"question_id": "q3", "answer": ""},
                ]
            ),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_score"] == 0.0

    def test_submit_invalid_exam_id(self) -> None:
        payload = self._payload()
        payload["exam_id"] = "no_colon"
        resp = _client().post("/api/submissions", json=payload)
        assert resp.status_code == 400

    def test_submit_invalid_date(self) -> None:
        payload = self._payload()
        payload["exam_id"] = "cau_giay:bad-date"
        resp = _client().post("/api/submissions", json=payload)
        assert resp.status_code == 400

    def test_submit_missing_exam(self) -> None:
        payload = self._payload()
        payload["exam_id"] = "unknown:2026-11-06"
        resp = _client().post("/api/submissions", json=payload)
        assert resp.status_code == 404
