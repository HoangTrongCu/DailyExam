"""Compose daily exams from template bank according to school style config."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from app.config import get_settings
from app.schemas import DifficultyLevel
from app.template_engine import RenderedQuestion, TemplateSpec, list_templates, render

ICT = timezone(timedelta(hours=7))


@dataclass
class ExamComposition:
    """A fully composed exam ready to persist."""

    id: str
    school_id: str
    exam_date: date
    duration_minutes: int
    questions: list[dict[str, Any]]  # serialisable question dicts (no correct answer!)
    answer_key: dict[str, dict[str, Any]]  # qid -> {correct, steps, narrative}
    gate_open_at: datetime
    gate_close_at: datetime


def _default_distribution() -> dict[DifficultyLevel, float]:
    return {
        DifficultyLevel.NB: 0.2,
        DifficultyLevel.TH: 0.3,
        DifficultyLevel.VD: 0.35,
        DifficultyLevel.VDC: 0.15,
    }


def compose_exam(
    school_id: str,
    exam_date: date,
    num_questions: int = 10,
    duration_minutes: int = 60,
    config: dict[str, Any] | None = None,
    seed: int | None = None,
) -> ExamComposition:
    """Build a daily exam for the given school and date."""
    config = config or {}
    rng = random.Random(seed if seed is not None else f"{school_id}:{exam_date.isoformat()}")

    distribution = _parse_distribution(config.get("difficulty_distribution")) or _default_distribution()
    chuyen_de_weights = config.get("chuyen_de_weights", {})

    counts = _allocate_counts(num_questions, distribution)
    questions: list[RenderedQuestion] = []

    for difficulty, n in counts.items():
        candidates = list_templates(difficulty=difficulty)
        if not candidates:
            # Fall back to any difficulty
            candidates = list_templates()
        for _ in range(n):
            spec = _pick_template(candidates, chuyen_de_weights, rng)
            questions.append(render(spec, rng))

    rng.shuffle(questions)

    qlist: list[dict[str, Any]] = []
    answers: dict[str, dict[str, Any]] = {}
    for index, q in enumerate(questions, start=1):
        qid = f"q{index}"
        qlist.append(
            {
                "id": qid,
                "index": index,
                "type": q.question_type.value,
                "difficulty": q.difficulty.value,
                "chuyen_de": q.chuyen_de,
                "content": q.content,
                "choices": q.choices,
                "max_score": q.max_score,
                "unit": q.unit,
                "template_id": q.template_id,
            }
        )
        answers[qid] = {
            "correct": q.correct_answer,
            "steps": q.solution_steps,
            "narrative": q.solution_narrative,
        }

    settings = get_settings()
    gate_open = datetime.combine(exam_date, time(settings.gate_open_hour, 0), tzinfo=ICT)
    gate_close = datetime.combine(exam_date, time(settings.gate_close_hour, 0), tzinfo=ICT)

    return ExamComposition(
        id=f"{school_id}:{exam_date.isoformat()}",
        school_id=school_id,
        exam_date=exam_date,
        duration_minutes=duration_minutes,
        questions=qlist,
        answer_key=answers,
        gate_open_at=gate_open,
        gate_close_at=gate_close,
    )


def _parse_distribution(raw: dict[str, float] | None) -> dict[DifficultyLevel, float] | None:
    if not raw:
        return None
    return {DifficultyLevel(k): float(v) for k, v in raw.items()}


def _allocate_counts(total: int, distribution: dict[DifficultyLevel, float]) -> dict[DifficultyLevel, int]:
    total_weight = sum(distribution.values()) or 1.0
    raw = {level: (weight / total_weight) * total for level, weight in distribution.items()}
    counts = {level: int(v) for level, v in raw.items()}
    remainder = total - sum(counts.values())
    # Distribute remainder by largest fractional part
    fracs = sorted(raw.items(), key=lambda kv: (kv[1] - int(kv[1])), reverse=True)
    for level, _ in fracs:
        if remainder <= 0:
            break
        counts[level] += 1
        remainder -= 1
    return counts


def _pick_template(
    specs: list[TemplateSpec],
    chuyen_de_weights: dict[str, float],
    rng: random.Random,
) -> TemplateSpec:
    weights = [max(chuyen_de_weights.get(spec.chuyen_de, 1.0), 0.1) for spec in specs]
    return rng.choices(specs, weights=weights, k=1)[0]
