"""Grading: MCQ, numeric, essay (with optional LLM)."""

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings
from app.math_engine import numbers_equal


@dataclass
class GradeResult:
    question_id: str
    score: float
    max_score: float
    is_correct: bool
    feedback: str | None = None
    confidence: float = 1.0


def grade_multiple_choice(qid: str, answer: str, correct: str, max_score: float) -> GradeResult:
    stu = (answer or "").strip().upper()
    cor = (correct or "").strip().upper()
    ok = bool(stu) and stu == cor
    return GradeResult(
        question_id=qid,
        score=max_score if ok else 0.0,
        max_score=max_score,
        is_correct=ok,
        feedback=None if ok else f"Đáp án đúng là {correct}",
    )


def grade_numeric(qid: str, answer: str, correct: str, max_score: float) -> GradeResult:
    ok = numbers_equal(answer, correct)
    return GradeResult(
        question_id=qid,
        score=max_score if ok else 0.0,
        max_score=max_score,
        is_correct=ok,
        feedback=None if ok else f"Đáp án đúng: {correct}",
        confidence=0.99,
    )


_WORD = re.compile(r"\w+", re.UNICODE)


def _tokens(s: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD.finditer(s) if len(m.group(0)) > 1}


def grade_essay_mock(qid: str, answer: str, reference: dict[str, Any], max_score: float) -> GradeResult:
    """Fallback rule-based essay grader."""
    if not answer.strip():
        return GradeResult(qid, 0.0, max_score, False, "Chưa có bài làm.", 1.0)
    correct = str(reference.get("correct", "")).strip()
    narrative = reference.get("narrative", "")
    steps = reference.get("steps", []) or []
    stoks = _tokens(answer)
    total = 0.0
    for step in steps:
        pts = float(step.get("points", 0.0))
        ref_tok = _tokens(step.get("formula", "") + " " + step.get("desc", ""))
        ratio = (len(ref_tok & stoks) / len(ref_tok)) if ref_tok else 0.0
        total += round(pts * ratio, 2)
    has_correct = correct and correct.lower() in answer.lower()
    if has_correct:
        total = max(total, max_score * 0.8)
    total = min(round(total, 2), max_score)
    fb = (
        ("Kết quả cuối của em đúng. " if has_correct else "Chưa thấy kết quả cuối trong bài. ")
        + "Lời giải chuẩn:\n" + narrative
    )
    return GradeResult(qid, total, max_score, has_correct, fb, 0.65 if has_correct else 0.5)


def grade_essay_llm(qid: str, answer: str, reference: dict[str, Any], question: str, max_score: float) -> GradeResult:
    """Call Claude Haiku for essay grading. Falls back to mock on error."""
    settings = get_settings()
    if settings.llm_mock_mode or not settings.anthropic_api_key:
        return grade_essay_mock(qid, answer, reference, max_score)

    prompt = (
        "Bạn là giáo viên Toán tiểu học. Chấm bài tự luận dựa trên lời giải chuẩn.\n"
        "Chấp nhận cách giải khác nếu logic đúng và đáp số đúng.\n"
        f"Trả về JSON: {{\"score\": float, \"confidence\": 0-1, \"feedback\": string}}.\n\n"
        f"Đề bài: {question}\n\n"
        f"Lời giải chuẩn ({max_score} điểm): {json.dumps(reference, ensure_ascii=False)}\n\n"
        f"Bài làm HS: {answer}\n"
    )
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": settings.llm_model, "max_tokens": 512, "messages": [{"role": "user", "content": prompt}]},
            timeout=30.0,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"]
        obj = json.loads(text[text.find("{"): text.rfind("}") + 1])
        return GradeResult(
            qid,
            min(float(obj.get("score", 0)), max_score),
            max_score,
            float(obj.get("score", 0)) >= max_score * 0.9,
            str(obj.get("feedback", "")),
            float(obj.get("confidence", 0.8)),
        )
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValueError):
        return grade_essay_mock(qid, answer, reference, max_score)


def grade_question(question: dict, answer: str, reference: dict) -> GradeResult:
    qid = question["id"]
    max_score = float(question["max_score"])
    qtype = question["type"]
    correct = reference.get("correct", "")

    if reference.get("disabled"):
        return GradeResult(qid, 0.0, 0.0, True, "Câu bị vô hiệu — không tính điểm", 1.0)

    if qtype == "multiple_choice":
        return grade_multiple_choice(qid, answer, correct, max_score)
    if qtype == "numeric":
        return grade_numeric(qid, answer, correct, max_score)
    if qtype == "essay":
        return grade_essay_llm(qid, answer, reference, question["content"], max_score)
    raise ValueError(f"Unknown type: {qtype}")
