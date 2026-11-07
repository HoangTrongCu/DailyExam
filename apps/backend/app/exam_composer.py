"""Compose daily exam from blueprint."""

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from app.template_engine import TemplateSpec, list_templates, load_all_templates, render

ICT = timezone(timedelta(hours=7))


@dataclass
class ExamComposition:
    id: str
    school_id: str
    exam_date: date
    duration_minutes: int
    questions: list[dict[str, Any]]
    answer_key: dict[str, dict[str, Any]]
    gate_open_at: datetime
    gate_close_at: datetime


DEFAULT_BLUEPRINT = {
    "exam_duration_minutes": 60,
    "total_questions": 10,
    "difficulty_distribution": {"NB": 0.2, "TH": 0.3, "VD": 0.35, "VDC": 0.15},
    "question_type_distribution": {"multiple_choice": 5, "numeric": 3, "essay": 2},
    "chuyen_de_weights": {},
}


def compose_exam(
    school_id: str,
    exam_date: date,
    blueprint: dict | None = None,
    seed: int | str | None = None,
) -> ExamComposition:
    """Compose exam per blueprint. Falls back to DEFAULT_BLUEPRINT for missing fields."""
    load_all_templates()
    bp = {**DEFAULT_BLUEPRINT, **(blueprint or {})}
    rng = random.Random(seed if seed is not None else f"{school_id}:{exam_date.isoformat()}")

    type_dist = bp["question_type_distribution"]
    qtype_slots: list[str] = []
    for qtype, count in type_dist.items():
        qtype_slots.extend([qtype] * count)

    # If total_questions differs from sum of type dist, pad or trim
    total = bp["total_questions"]
    if len(qtype_slots) < total:
        qtype_slots.extend(["multiple_choice"] * (total - len(qtype_slots)))
    qtype_slots = qtype_slots[:total]
    rng.shuffle(qtype_slots)

    weights = bp.get("chuyen_de_weights", {})
    questions: list = []
    for qtype in qtype_slots:
        candidates = list_templates(question_type=qtype)
        if not candidates:
            candidates = list_templates()
        spec = _weighted_pick(candidates, weights, rng)
        questions.append(render(spec, rng))

    qlist, akey = [], {}
    for idx, q in enumerate(questions, start=1):
        qid = f"q{idx}"
        qlist.append({
            "id": qid,
            "index": idx,
            "type": q.question_type,
            "difficulty": q.difficulty,
            "chuyen_de": q.chuyen_de,
            "content": q.content,
            "choices": q.choices,
            "max_score": q.max_score,
            "unit": q.unit,
            "template_id": q.template_id,
        })
        akey[qid] = {
            "correct": q.correct_answer,
            "steps": q.solution_steps,
            "narrative": q.solution_narrative,
            "disabled": False,
        }

    gate_open = datetime.combine(exam_date, time(0, 0), tzinfo=ICT)
    gate_close = datetime.combine(exam_date + timedelta(days=1), time(0, 0), tzinfo=ICT)
    return ExamComposition(
        id=f"{school_id}:{exam_date.isoformat()}",
        school_id=school_id,
        exam_date=exam_date,
        duration_minutes=bp["exam_duration_minutes"],
        questions=qlist,
        answer_key=akey,
        gate_open_at=gate_open,
        gate_close_at=gate_close,
    )


def _weighted_pick(specs: list[TemplateSpec], weights: dict[str, float], rng: random.Random) -> TemplateSpec:
    w = [max(weights.get(s.chuyen_de, 1.0), 0.1) for s in specs]
    return rng.choices(specs, weights=w, k=1)[0]
