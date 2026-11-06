"""Reference-based essay grader.

Uses Claude API when ``anthropic_api_key`` is set, otherwise falls back to a
rule-based scorer suitable for local dev and CI.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings


@dataclass
class EssayGrade:
    score: float
    confidence: float
    feedback: str
    step_scores: list[dict[str, Any]]


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD_RE.finditer(text) if len(m.group(0)) > 1}


def mock_grade(student_answer: str, reference: dict[str, Any], max_score: float) -> EssayGrade:
    """Rule-based essay scorer: keyword overlap on each step + numeric answer check."""
    steps = reference.get("steps", []) or []
    correct = str(reference.get("correct", "")).strip()
    narrative = reference.get("narrative", "")

    if not student_answer.strip():
        return EssayGrade(0.0, 1.0, "Chưa có bài làm.", [])

    student_lower = student_answer.lower()
    student_toks = _tokens(student_answer)
    step_scores: list[dict[str, Any]] = []
    total = 0.0

    answer_in_text = correct and correct.lower() in student_lower
    for step in steps:
        pts = float(step.get("points", 0.0))
        step_toks = _tokens(step.get("formula", "") + " " + step.get("desc", ""))
        if not step_toks:
            overlap_ratio = 0.0
        else:
            overlap_ratio = len(step_toks & student_toks) / len(step_toks)
        awarded = round(pts * overlap_ratio, 2)
        step_scores.append({"desc": step.get("desc"), "max": pts, "awarded": awarded})
        total += awarded

    # Bonus / cap based on final numeric answer presence
    if answer_in_text:
        total = max(total, max_score * 0.8)
    total = min(round(total, 2), max_score)

    feedback = (
        "Tự động chấm theo mẫu lời giải. "
        + ("Kết quả cuối của em đúng. " if answer_in_text else "Chưa thấy kết quả cuối trong bài. ")
        + f"Lời giải chuẩn:\n{narrative}"
    )
    return EssayGrade(total, 0.65 if answer_in_text else 0.5, feedback, step_scores)


def _build_prompt(student_answer: str, reference: dict[str, Any], question: str, max_score: float) -> list[dict[str, Any]]:
    system = (
        "Bạn là giáo viên chấm Toán tiểu học/THCS. Chấm bài tự luận theo lời giải chuẩn, "
        "chia điểm theo bước. Chấp nhận cách giải khác nếu logic đúng và đáp số đúng. "
        "Trả về JSON với các trường: total_score (float), confidence (0-1), feedback (string), "
        "step_scores (list of {desc, max, awarded})."
    )
    user = (
        f"## Đề bài\n{question}\n\n"
        f"## Lời giải chuẩn ({max_score} điểm)\n{json.dumps(reference, ensure_ascii=False)}\n\n"
        f"## Bài làm học sinh\n{student_answer}\n\n"
        f"Chấm bài. Trả về JSON."
    )
    return [{"role": "user", "content": [{"type": "text", "text": system + "\n\n" + user}]}]


def llm_grade(student_answer: str, reference: dict[str, Any], question: str, max_score: float) -> EssayGrade:
    """Call Claude API to grade (used when llm_mock_mode is False)."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return mock_grade(student_answer, reference, max_score)
    payload = {
        "model": settings.llm_model,
        "max_tokens": 1024,
        "messages": _build_prompt(student_answer, reference, question, max_score),
    }
    try:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        text = data["content"][0]["text"]
        parsed = json.loads(_extract_json(text))
        return EssayGrade(
            score=min(float(parsed.get("total_score", 0.0)), max_score),
            confidence=float(parsed.get("confidence", 0.8)),
            feedback=str(parsed.get("feedback", "")),
            step_scores=parsed.get("step_scores", []),
        )
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValueError):
        return mock_grade(student_answer, reference, max_score)


def _extract_json(text: str) -> str:
    """Pull the first JSON object substring from text."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON in LLM response")
    return text[start : end + 1]


def grade_essay(
    student_answer: str,
    reference: dict[str, Any],
    question: str,
    max_score: float,
) -> EssayGrade:
    """Dispatch to LLM or mock based on configuration."""
    settings = get_settings()
    if settings.llm_mock_mode or not settings.anthropic_api_key:
        return mock_grade(student_answer, reference, max_score)
    return llm_grade(student_answer, reference, question, max_score)
