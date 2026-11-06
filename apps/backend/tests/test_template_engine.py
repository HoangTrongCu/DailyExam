"""Tests for template engine and bundled templates."""

import random

import pytest

from app.template_engine import (
    TemplateError,
    TemplateSpec,
    clear_registry,
    get_template,
    list_templates,
    load_all_templates,
    register,
    render,
)
from app.schemas import DifficultyLevel, QuestionType


@pytest.fixture(autouse=True)
def _ensure_templates_loaded():
    """Make sure templates are registered. Idempotent."""
    if not list_templates():
        import app.templates.loader as loader
        loader._loaded = False
        load_all_templates()
    yield


def test_load_all_registers_many() -> None:
    specs = list_templates()
    assert len(specs) >= 15


def test_list_by_chuyen_de() -> None:
    specs = list_templates(chuyen_de="trung_binh_cong")
    assert specs and all(s.chuyen_de == "trung_binh_cong" for s in specs)


def test_list_by_difficulty() -> None:
    specs = list_templates(difficulty=DifficultyLevel.NB)
    assert all(s.difficulty == DifficultyLevel.NB for s in specs)


def test_get_known_template() -> None:
    spec = get_template("tbc_3so_tim_so_thieu")
    assert spec.chuyen_de == "trung_binh_cong"


def test_get_unknown_template() -> None:
    with pytest.raises(KeyError):
        get_template("nonexistent")


def test_render_produces_valid_question() -> None:
    spec = get_template("tbc_3so_tim_so_thieu")
    q = render(spec, random.Random(1))
    assert q.correct_answer
    assert q.content
    assert q.max_score > 0
    assert q.question_type == QuestionType.NUMERIC


def test_render_all_bundled_templates() -> None:
    rng = random.Random(42)
    for spec in list_templates():
        q = render(spec, rng)
        assert q.correct_answer
        assert q.content


def test_duplicate_register_raises() -> None:
    spec = get_template("tbc_3so_tim_so_thieu")
    # Try to register a copy (same id) — should raise
    with pytest.raises(TemplateError):
        register(spec)
    # Clean state so later tests still work (re-insert because register raises before mutation)
    # Note: the registry check happens before any write so no cleanup needed.


def test_render_max_attempts_raises() -> None:
    """A template whose sampler always raises should fail after retries."""

    def bad_sampler(rng):
        raise TemplateError("always bad")

    spec = TemplateSpec(
        id="always_bad",
        chuyen_de="x",
        dang_bai="y",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=bad_sampler,
        solver=lambda p: {"answer": 0},
        content_builder=lambda p, s: "x",
    )
    with pytest.raises(TemplateError):
        render(spec, random.Random(0), max_attempts=3)


def test_template_spec_with_choices_builder() -> None:
    spec = get_template("tbc_tinh_tbc_cua_n_so")
    q = render(spec, random.Random(5))
    assert q.choices is not None
    assert len(q.choices) == 4
