"""Template engine: sample params, run solvers, render question text.

Each template is a Python module under ``app.templates`` that exposes a ``TEMPLATE``
constant. See ``core_templates/README.md`` for the schema.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable

from app.schemas import DifficultyLevel, QuestionType


@dataclass(frozen=True)
class RenderedQuestion:
    """A fully-rendered question ready to be inserted into an exam."""

    template_id: str
    chuyen_de: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    content: str
    choices: list[str] | None
    correct_answer: str
    solution_steps: list[dict[str, Any]]
    solution_narrative: str
    max_score: float
    unit: str | None


class TemplateError(ValueError):
    """Raised when a template definition is invalid or constraints unsatisfiable."""


@dataclass
class TemplateSpec:
    """Template spec. Pass this to ``render`` with an RNG to produce a question."""

    id: str
    chuyen_de: str
    dang_bai: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    max_score: float
    sampler: Callable[[random.Random], dict[str, Any]]
    solver: Callable[[dict[str, Any]], dict[str, Any]]
    content_builder: Callable[[dict[str, Any], dict[str, Any]], str]
    choices_builder: Callable[[dict[str, Any], dict[str, Any]], list[str]] | None = None
    solution_steps_builder: Callable[[dict[str, Any], dict[str, Any]], list[dict[str, Any]]] | None = None
    narrative_builder: Callable[[dict[str, Any], dict[str, Any]], str] | None = None
    unit: str | None = None


def render(spec: TemplateSpec, rng: random.Random | None = None, max_attempts: int = 25) -> RenderedQuestion:
    """Render a spec into a question. Retries on constraint failures."""
    rng = rng or random.Random()
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            params = spec.sampler(rng)
            solution = spec.solver(params)
            content = spec.content_builder(params, solution)
            choices = spec.choices_builder(params, solution) if spec.choices_builder else None
            steps = spec.solution_steps_builder(params, solution) if spec.solution_steps_builder else []
            narrative = spec.narrative_builder(params, solution) if spec.narrative_builder else ""
            correct = str(solution.get("answer", ""))
            return RenderedQuestion(
                template_id=spec.id,
                chuyen_de=spec.chuyen_de,
                difficulty=spec.difficulty,
                question_type=spec.question_type,
                content=content,
                choices=choices,
                correct_answer=correct,
                solution_steps=steps,
                solution_narrative=narrative,
                max_score=spec.max_score,
                unit=spec.unit,
            )
        except TemplateError as exc:
            last_error = exc
            continue
    raise TemplateError(f"Could not render {spec.id} after {max_attempts} attempts: {last_error}")


# ─── Registry ─────────────────────────────────────────────────────────────
_REGISTRY: dict[str, TemplateSpec] = {}


def register(spec: TemplateSpec) -> TemplateSpec:
    """Register a template in the global registry."""
    if spec.id in _REGISTRY:
        raise TemplateError(f"Duplicate template id: {spec.id}")
    _REGISTRY[spec.id] = spec
    return spec


def get_template(template_id: str) -> TemplateSpec:
    if template_id not in _REGISTRY:
        raise KeyError(f"Unknown template: {template_id}")
    return _REGISTRY[template_id]


def list_templates(chuyen_de: str | None = None, difficulty: DifficultyLevel | None = None) -> list[TemplateSpec]:
    specs = list(_REGISTRY.values())
    if chuyen_de:
        specs = [s for s in specs if s.chuyen_de == chuyen_de]
    if difficulty:
        specs = [s for s in specs if s.difficulty == difficulty]
    return specs


def clear_registry() -> None:
    """Testing helper — clear all registered templates."""
    _REGISTRY.clear()


def load_all_templates() -> int:
    """Import template modules so they self-register. Idempotent."""
    from app.templates import loader
    return loader.load_all()
