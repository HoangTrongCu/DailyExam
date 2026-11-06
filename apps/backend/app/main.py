"""FastAPI application — full feature set."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import __version__, models
from app.api_schemas import (
    AnalyticsEntry,
    LoginRequest,
    RegisterRequest,
    SubmissionRequestV2,
    TokenResponse,
)
from app.auth import create_access_token, get_current_user, require_role
from app.config import get_settings
from app.db import get_db, init_db
from app.schemas import HealthResponse
from app.services import exam_service, submission_service, user_service
from app.startup import seed_initial_data


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="DailyExam — automated daily exam generation and grading.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup() -> None:
        init_db()
        exam_service.ensure_templates_loaded()
        seed_initial_data()

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", environment=settings.environment, version=__version__)

    # ─── Auth ────────────────────────────────────────────────
    @app.post("/api/auth/register", response_model=TokenResponse, tags=["auth"])
    def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
        try:
            user = user_service.create_user(
                db,
                email=payload.email,
                password=payload.password,
                full_name=payload.full_name,
                role=payload.role,
                school_id=payload.school_id,
                grade=payload.grade,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        token = create_access_token(user)
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            role=user.role,
            full_name=user.full_name,
            school_id=user.school_id,
        )

    @app.post("/api/auth/login", response_model=TokenResponse, tags=["auth"])
    def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
        user = user_service.authenticate(db, payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return TokenResponse(
            access_token=create_access_token(user),
            user_id=user.id,
            role=user.role,
            full_name=user.full_name,
            school_id=user.school_id,
        )

    @app.get("/api/auth/me", tags=["auth"])
    def me(user: models.User = Depends(get_current_user)) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "school_id": user.school_id,
        }

    # ─── Schools ─────────────────────────────────────────────
    @app.get("/api/schools", tags=["schools"])
    def list_schools(db: Session = Depends(get_db)) -> list[dict]:
        return [
            {"id": s.id, "name": s.name, "short_name": s.short_name, "grade_levels": s.grade_levels}
            for s in db.query(models.School).all()
        ]

    @app.get("/api/schools/{school_id}", tags=["schools"])
    def get_school(school_id: str, db: Session = Depends(get_db)) -> dict:
        school = db.query(models.School).filter_by(id=school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        return {
            "id": school.id,
            "name": school.name,
            "short_name": school.short_name,
            "grade_levels": school.grade_levels,
            "config": school.config,
        }

    # ─── Exams ───────────────────────────────────────────────
    @app.get("/api/schools/{school_id}/exams/{exam_date}", tags=["exams"])
    def get_exam(school_id: str, exam_date: date, db: Session = Depends(get_db)) -> dict:
        exam = exam_service.get_daily_exam(db, school_id, exam_date)
        if not exam:
            exam = exam_service.generate_daily_exam(db, school_id, exam_date)
        return exam_service.public_view(exam)

    @app.post("/api/schools/{school_id}/exams/{exam_date}/generate", tags=["exams"])
    def generate_exam(
        school_id: str,
        exam_date: date,
        db: Session = Depends(get_db),
        _user: models.User = Depends(require_role("teacher", "admin")),
    ) -> dict:
        exam = exam_service.generate_daily_exam(db, school_id, exam_date)
        return exam_service.public_view(exam)

    # ─── Submissions ─────────────────────────────────────────
    @app.post("/api/submissions", tags=["grading"])
    def submit(
        payload: SubmissionRequestV2,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> dict:
        if ":" not in payload.exam_id:
            raise HTTPException(status_code=400, detail="Invalid exam id")
        school_id, date_str = payload.exam_id.split(":", 1)
        try:
            exam_date = date.fromisoformat(date_str)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid exam date") from exc
        exam = exam_service.get_daily_exam(db, school_id, exam_date)
        if not exam:
            exam = exam_service.generate_daily_exam(db, school_id, exam_date)
        submission = submission_service.submit_and_grade(db, exam, user, payload.answers)
        return _submission_view(submission)

    @app.get("/api/me/submissions", tags=["student"])
    def my_submissions(
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> list[dict]:
        return [_submission_view(s) for s in submission_service.student_history(db, user.id)]

    @app.get("/api/me/analytics", response_model=list[AnalyticsEntry], tags=["student"])
    def my_analytics(
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> list[AnalyticsEntry]:
        rows = submission_service.student_analytics(db, user.id)
        return [AnalyticsEntry(**r) for r in rows]

    # ─── Teacher ─────────────────────────────────────────────
    @app.get("/api/teacher/submissions", tags=["teacher"])
    def teacher_submissions(
        db: Session = Depends(get_db),
        user: models.User = Depends(require_role("teacher", "admin")),
    ) -> list[dict]:
        rows = (
            db.query(models.Submission)
            .join(models.User, models.Submission.student_id == models.User.id)
            .filter(models.User.school_id == user.school_id)
            .order_by(models.Submission.graded_at.desc())
            .limit(100)
            .all()
        )
        return [_submission_view(s) for s in rows]

    return app


def _submission_view(s: models.Submission) -> dict:
    return {
        "id": s.id,
        "exam_id": s.exam_id,
        "student_id": s.student_id,
        "total_score": s.total_score,
        "max_total_score": s.max_total_score,
        "percentage": s.percentage,
        "question_results": s.question_results,
        "graded_at": s.graded_at.isoformat() if s.graded_at else None,
    }


app = create_app()
