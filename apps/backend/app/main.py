"""FastAPI application entrypoint."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.grader import grade_question
from app.schemas import (
    DailyExam,
    GradingResult,
    HealthResponse,
    School,
    SubmissionRequest,
)
from app.store import correct_answer_for, get_daily_exam, get_school, list_schools


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Auto exam generation and grading platform for schools.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            environment=settings.environment,
            version=__version__,
        )

    @app.get("/api/schools", response_model=list[School], tags=["schools"])
    def api_list_schools() -> list[School]:
        return list_schools()

    @app.get("/api/schools/{school_id}", response_model=School, tags=["schools"])
    def api_get_school(school_id: str) -> School:
        school = get_school(school_id)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        return school

    @app.get(
        "/api/schools/{school_id}/exams/{exam_date}",
        response_model=DailyExam,
        tags=["exams"],
    )
    def api_get_daily_exam(school_id: str, exam_date: date) -> DailyExam:
        exam = get_daily_exam(school_id, exam_date)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        return exam

    @app.post("/api/submissions", response_model=GradingResult, tags=["grading"])
    def api_submit(payload: SubmissionRequest) -> GradingResult:
        if ":" not in payload.exam_id:
            raise HTTPException(status_code=400, detail="Invalid exam id")
        school_id, date_str = payload.exam_id.split(":", 1)
        try:
            exam_date = date.fromisoformat(date_str)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid exam date") from exc
        exam = get_daily_exam(school_id, exam_date)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        answers_by_qid = {a.question_id: a.answer for a in payload.answers}
        results = []
        for question in exam.questions:
            student_answer = answers_by_qid.get(question.id, "")
            correct = correct_answer_for(question.id)
            results.append(grade_question(question, student_answer, correct))
        total_score = round(sum(r.score for r in results), 2)
        max_total = round(sum(r.max_score for r in results), 2)
        percentage = round((total_score / max_total * 100) if max_total else 0.0, 2)
        return GradingResult(
            submission_id=str(uuid.uuid4()),
            exam_id=payload.exam_id,
            student_id=payload.student_id,
            total_score=total_score,
            max_total_score=max_total,
            percentage=percentage,
            question_results=results,
            graded_at=datetime.now(timezone.utc),
        )

    return app


app = create_app()
