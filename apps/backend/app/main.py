"""FastAPI main application — all endpoints per SDD §3."""

from datetime import date, datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import __version__, models
from app.api_schemas import (
    AppealRequest,
    AppealResolveRequest,
    AutosaveRequest,
    BlueprintUploadRequest,
    ForgotPasswordRequest,
    HealthResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SubmissionRequest,
    TokenResponse,
)
from app.auth import create_access_token, get_current_user, require_admin
from app.config import get_settings
from app.db import get_db, init_db
from app.services import appeal_service, exam_service, submission_service
from app.services.email_service import (
    build_result_email,
    build_reset_email,
    build_verify_email,
    send_email,
)
from app.services.user_service import (
    AuthError,
    authenticate_and_rotate_session,
    register_user,
    request_password_reset,
    reset_password,
    soft_delete,
    verify_email_token,
)
from app.startup import seed
from app.template_engine import load_all_templates


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=__version__)
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
        load_all_templates()
        seed()

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", environment=settings.environment, version=__version__)

    # ──────────── Auth ────────────
    @app.post("/api/auth/register")
    def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
        try:
            user, token = register_user(
                db, payload.email, payload.password, payload.full_name, payload.child_name,
            )
        except AuthError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if token:
            link = f"{settings.base_url}/verify/{token}"
            subject, html = build_verify_email(user.full_name, link)
            send_email(user.email, subject, html)
        return {"user_id": user.id, "status": user.status, "message": "Email xác minh đã được gửi"}

    @app.get("/api/auth/verify/{token}")
    def verify_email(token: str, db: Session = Depends(get_db)) -> dict:
        try:
            user = verify_email_token(db, token)
        except AuthError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True, "user_id": user.id}

    @app.post("/api/auth/login", response_model=TokenResponse)
    def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
        try:
            user, session_token = authenticate_and_rotate_session(db, payload.email, payload.password)
        except AuthError as exc:
            status_code = 403 if exc.code in {"pending_verify", "banned", "deleted"} else 401
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return TokenResponse(
            access_token=create_access_token(user, session_token),
            user_id=user.id,
            role=user.role,
            full_name=user.full_name,
        )

    @app.post("/api/auth/forgot-password")
    def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
        token = request_password_reset(db, payload.email)
        if token:
            user = db.query(models.User).filter_by(email=payload.email).first()
            if user:
                link = f"{settings.base_url}/reset/{token}"
                subject, html = build_reset_email(user.full_name, link)
                send_email(user.email, subject, html)
        return {"message": "Nếu email tồn tại, link đặt lại mật khẩu đã được gửi"}

    @app.post("/api/auth/reset-password")
    def reset_pw(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
        try:
            reset_password(db, payload.token, payload.new_password)
        except AuthError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True}

    @app.get("/api/auth/me")
    def me(user: models.User = Depends(get_current_user)) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "child_name": user.child_name,
            "role": user.role,
        }

    @app.delete("/api/me")
    def delete_me(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
        soft_delete(db, user.id)
        return {"success": True}

    # ──────────── Schools & Exams ────────────
    @app.get("/api/schools")
    def schools(db: Session = Depends(get_db)) -> list[dict]:
        return [{"id": s.id, "name": s.name, "short_name": s.short_name} for s in db.query(models.School).all()]

    @app.get("/api/exams/today")
    def exams_today(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)) -> list[dict]:
        from app.exam_composer import ICT
        today = datetime.now(ICT).date()
        results = []
        for school in db.query(models.School).all():
            exam = db.query(models.Exam).filter_by(school_id=school.id, exam_date=today).first()
            if not exam:
                try:
                    exam = exam_service.generate_daily_exam(db, school.id, today)
                except ValueError:
                    continue
            results.append({
                "exam_id": exam.id,
                "school_id": school.id,
                "school_name": school.name,
                "status": exam.status,
                "duration_minutes": exam.duration_minutes,
                "exam_date": exam.exam_date.isoformat(),
                "num_questions": len(exam.exam_data.get("questions", [])),
            })
        return results

    @app.get("/api/exams/{exam_id}")
    def get_exam(exam_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)) -> dict:
        exam = db.query(models.Exam).filter_by(id=exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        if exam.status == "closed":
            raise HTTPException(status_code=403, detail="Đề đã đóng vĩnh viễn")
        return exam_service.public_view(exam)

    @app.post("/api/exams/{exam_id}/submit")
    def submit(
        exam_id: str,
        payload: SubmissionRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> dict:
        exam = db.query(models.Exam).filter_by(id=exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        if exam.status == "closed":
            raise HTTPException(status_code=403, detail="Đề đã đóng vĩnh viễn")
        sub = submission_service.submit_and_grade(db, exam, user, payload.answers)
        # Fire email (sync, mock)
        link = f"{settings.base_url}/history"
        subject, html = build_result_email(
            user.full_name, user.child_name or user.full_name,
            exam.school_id, sub.total_score, sub.max_total_score, link,
        )
        send_email(user.email, subject, html)
        return _submission_view(sub)

    @app.post("/api/exams/{exam_id}/autosave")
    def autosave(
        exam_id: str,
        payload: AutosaveRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> dict:
        # For now, autosave is accepted but not persisted as draft (keeps MVP simple)
        _ = (exam_id, payload, db, user)
        return {"saved": True, "count": len(payload.answers)}

    # ──────────── Submissions / History / Analytics ────────────
    @app.get("/api/me/submissions")
    def my_submissions(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
        return [_submission_view(s) for s in submission_service.student_history(db, user.id)]

    @app.get("/api/me/submissions/{submission_id}")
    def my_submission(submission_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
        sub = db.query(models.Submission).filter_by(id=submission_id, student_id=user.id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Not found")
        exam = db.query(models.Exam).filter_by(id=sub.exam_id).first()
        return {**_submission_view(sub), "exam": exam_service.public_view(exam) if exam else None,
                "answer_key": exam.answer_key if exam else {}}

    @app.get("/api/me/analytics")
    def my_analytics(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
        return submission_service.student_analytics(db, user.id)

    @app.get("/api/rankings/{school_id}")
    def rankings(
        school_id: str,
        period: str = "total",
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        top = submission_service.rankings_for_school(db, school_id, period)
        my_rank = next((e["rank"] for e in top if e["student_id"] == user.id), None)
        return {"period": period, "school_id": school_id, "top": top, "my_rank": my_rank}

    # ──────────── Appeals ────────────
    @app.post("/api/appeals")
    def file_appeal_endpoint(
        payload: AppealRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user),
    ) -> dict:
        try:
            ap = appeal_service.file_appeal(db, payload.submission_id, user.id, payload.question_id, payload.reason)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"appeal_id": ap.id, "status": ap.status}

    @app.get("/api/me/appeals")
    def my_appeals(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
        rows = db.query(models.Appeal).filter_by(student_id=user.id).order_by(models.Appeal.created_at.desc()).all()
        return [_appeal_view(a) for a in rows]

    # ──────────── Admin ────────────
    @app.get("/api/admin/appeals")
    def admin_appeals(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)) -> list[dict]:
        return [_appeal_view(a) for a in appeal_service.list_open_appeals(db)]

    @app.post("/api/admin/appeals/{appeal_id}/resolve")
    def admin_resolve(
        appeal_id: str,
        payload: AppealResolveRequest,
        _admin: models.User = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> dict:
        try:
            return appeal_service.resolve_appeal(db, appeal_id, payload.action, payload.admin_note, payload.new_correct)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/admin/blueprints")
    def admin_upload_blueprint(
        payload: BlueprintUploadRequest,
        _admin: models.User = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> dict:
        prev = db.query(models.Blueprint).filter_by(school_id=payload.school_id, is_active=True).first()
        version = (prev.version + 1) if prev else 1
        if prev:
            prev.is_active = False
        bp = models.Blueprint(school_id=payload.school_id, version=version, structure=payload.structure, is_active=True)
        db.add(bp)
        db.commit()
        db.refresh(bp)
        return {"blueprint_id": bp.id, "version": bp.version}

    @app.post("/api/admin/exams/{school_id}/regenerate")
    def admin_regenerate(
        school_id: str,
        _admin: models.User = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> dict:
        from app.exam_composer import ICT
        today = datetime.now(ICT).date()
        existing = db.query(models.Exam).filter_by(school_id=school_id, exam_date=today).first()
        if existing:
            db.delete(existing)
            db.commit()
        exam = exam_service.generate_daily_exam(db, school_id, today)
        return exam_service.public_view(exam)

    @app.get("/api/admin/stats")
    def admin_stats(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
        from app.exam_composer import ICT
        today = datetime.now(ICT).date()
        return {
            "total_users": db.query(models.User).filter(models.User.role == "student").count(),
            "total_submissions": db.query(models.Submission).count(),
            "open_appeals": db.query(models.Appeal).filter_by(status="open").count(),
            "exams_today": db.query(models.Exam).filter_by(exam_date=today).count(),
        }

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
        "counts_for_ranking": s.counts_for_ranking,
        "graded_at": s.graded_at.isoformat() if s.graded_at else None,
    }


def _appeal_view(a: models.Appeal) -> dict:
    return {
        "id": a.id,
        "submission_id": a.submission_id,
        "student_id": a.student_id,
        "question_id": a.question_id,
        "reason": a.reason,
        "status": a.status,
        "admin_note": a.admin_note,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
    }


app = create_app()
