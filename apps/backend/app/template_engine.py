"""Template engine. Each template module calls register() at import time."""

import random
from dataclasses import dataclass
from typing import Any, Callable


class TemplateError(ValueError):
    pass


@dataclass(frozen=True)
class RenderedQuestion:
    template_id: str
    chuyen_de: str
    difficulty: str
    question_type: str
    content: str
    choices: list[str] | None
    correct_answer: str
    solution_steps: list[dict[str, Any]]
    solution_narrative: str
    max_score: float
    unit: str | None


@dataclass
class TemplateSpec:
    id: str
    chuyen_de: str
    difficulty: str
    question_type: str
    max_score: float
    sampler: Callable[[random.Random], dict]
    solver: Callable[[dict], dict]
    content_builder: Callable[[dict, dict], str]
    choices_builder: Callable[[dict, dict], list[str]] | None = None
    steps_builder: Callable[[dict, dict], list[dict]] | None = None
    narrative_builder: Callable[[dict, dict], str] | None = None
    unit: str | None = None


_REGISTRY: dict[str, TemplateSpec] = {}


def register(spec: TemplateSpec) -> TemplateSpec:
    if spec.id in _REGISTRY:
        raise TemplateError(f"Duplicate template id: {spec.id}")
    _REGISTRY[spec.id] = spec
    return spec


def get_template(template_id: str) -> TemplateSpec:
    if template_id not in _REGISTRY:
        raise KeyError(template_id)
    return _REGISTRY[template_id]


def list_templates(chuyen_de: str | None = None, difficulty: str | None = None, question_type: str | None = None) -> list[TemplateSpec]:
    specs = list(_REGISTRY.values())
    if chuyen_de:
        specs = [s for s in specs if s.chuyen_de == chuyen_de]
    if difficulty:
        specs = [s for s in specs if s.difficulty == difficulty]
    if question_type:
        specs = [s for s in specs if s.question_type == question_type]
    return specs


def clear_registry() -> None:
    _REGISTRY.clear()


def render(spec: TemplateSpec, rng: random.Random, max_attempts: int = 25) -> RenderedQuestion:
    last_err: Exception | None = None
    for _ in range(max_attempts):
        try:
            params = spec.sampler(rng)
            solution = spec.solver(params)
            content = spec.content_builder(params, solution)
            choices = spec.choices_builder(params, solution) if spec.choices_builder else None
            steps = spec.steps_builder(params, solution) if spec.steps_builder else []
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
            last_err = exc
    raise TemplateError(f"Failed after {max_attempts} attempts: {last_err}")


_loaded = False


def load_all_templates() -> int:
    global _loaded
    if _loaded and _REGISTRY:
        return len(_REGISTRY)
    from app.templates import arithmetic, geometry, word_problems  # noqa: F401
    _loaded = True
    return len(_REGISTRY)
