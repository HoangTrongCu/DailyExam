"""Pydantic schemas for API request/response models."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Mức độ bài toán theo chuẩn SGK Việt Nam."""

    NB = "NB"  # Nhận biết
    TH = "TH"  # Thông hiểu
    VD = "VD"  # Vận dụng
    VDC = "VDC"  # Vận dụng cao


class QuestionType(str, Enum):
    """Loại câu hỏi."""

    MULTIPLE_CHOICE = "multiple_choice"
    NUMERIC = "numeric"
    ESSAY = "essay"


class ExamStatus(str, Enum):
    """Trạng thái bài thi của ngày."""

    GENERATING = "generating"
    READY = "ready"
    OPEN = "open"
    CLOSED = "closed"
    RELEASED = "released"


class School(BaseModel):
    """Thông tin trường."""

    id: str
    name: str
    short_name: str
    grade_levels: list[str]


class Question(BaseModel):
    """1 câu hỏi trong đề thi."""

    id: str
    index: int
    type: QuestionType
    difficulty: DifficultyLevel
    chuyen_de: str
    content: str
    max_score: float = Field(gt=0, le=10)
    choices: list[str] | None = None
    unit: str | None = None


class DailyExam(BaseModel):
    """Đề thi của 1 ngày."""

    id: str
    school_id: str
    exam_date: date
    status: ExamStatus
    total_score: float
    duration_minutes: int
    questions: list[Question]
    gate_open_at: datetime
    gate_close_at: datetime


class StudentAnswer(BaseModel):
    """Đáp án của HS cho 1 câu."""

    question_id: str
    answer: str


class SubmissionRequest(BaseModel):
    """Request nộp bài của HS."""

    exam_id: str
    student_id: str
    answers: list[StudentAnswer]


class QuestionResult(BaseModel):
    """Kết quả chấm của 1 câu."""

    question_id: str
    score: float
    max_score: float
    is_correct: bool
    feedback: str | None = None
    confidence: float = Field(ge=0, le=1)


class GradingResult(BaseModel):
    """Kết quả chấm toàn bài."""

    submission_id: str
    exam_id: str
    student_id: str
    total_score: float
    max_total_score: float
    percentage: float
    question_results: list[QuestionResult]
    graded_at: datetime


class HealthResponse(BaseModel):
    """Health check."""

    status: str
    environment: str
    version: str
