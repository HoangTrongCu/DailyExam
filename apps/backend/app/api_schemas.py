"""Pydantic schemas for API."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1)
    child_name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str


class SubmissionRequest(BaseModel):
    answers: dict[str, str]


class AutosaveRequest(BaseModel):
    answers: dict[str, str]


class AppealRequest(BaseModel):
    submission_id: str
    question_id: str
    reason: str = Field(min_length=3, max_length=500)


class AppealResolveRequest(BaseModel):
    action: str  # 'accept' | 'reject'
    admin_note: str | None = None
    new_correct: str | None = None


class BlueprintUploadRequest(BaseModel):
    school_id: str
    structure: dict


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
