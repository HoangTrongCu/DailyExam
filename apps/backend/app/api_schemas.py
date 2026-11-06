"""Additional API request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1)
    role: str = Field(default="student")
    school_id: str | None = None
    grade: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str
    school_id: str | None = None


class SubmissionRequestV2(BaseModel):
    exam_id: str
    answers: dict[str, str]


class AnalyticsEntry(BaseModel):
    chuyen_de: str
    attempts: int
    correct: int
    accuracy: float
    average_score_10: float
