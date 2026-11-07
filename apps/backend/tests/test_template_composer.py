"""Tests for template engine, templates, and composer."""

import random
from datetime import date

import pytest

from app.exam_composer import compose_exam
from app.template_engine import (
    TemplateError,
    TemplateSpec,
    get_template,
    list_templates,
    render,
)


class TestRegistry:
    def test_many_loaded(self):
        assert len(list_templates()) >= 10

    def test_filter_chuyen_de(self):
        specs = list_templates(chuyen_de="trung_binh_cong")
        assert specs and all(s.chuyen_de == "trung_binh_cong" for s in specs)

    def test_filter_difficulty(self):
        for lvl in ("NB", "TH", "VD"):
            specs = list_templates(difficulty=lvl)
            assert all(s.difficulty == lvl for s in specs)

    def test_filter_qtype(self):
        for t in ("multiple_choice", "numeric", "essay"):
            for s in list_templates(question_type=t):
                assert s.question_type == t

    def test_get_known(self):
        assert get_template("tbc_tim_so_thieu").chuyen_de == "trung_binh_cong"

    def test_get_unknown(self):
        with pytest.raises(KeyError):
            get_template("nonexistent")


class TestRender:
    def test_all_render_ok(self):
        rng = random.Random(42)
        for spec in list_templates():
            q = render(spec, rng)
            assert q.correct_answer
            assert q.content
            assert q.max_score > 0

    def test_retry_eventually_fails(self):
        def bad(rng):
            raise TemplateError("nope")
        spec = TemplateSpec(
            id="bad", chuyen_de="x", difficulty="NB", question_type="numeric", max_score=1,
            sampler=bad, solver=lambda p: {"answer": 0}, content_builder=lambda p, s: "x",
        )
        with pytest.raises(TemplateError):
            render(spec, random.Random(0), max_attempts=2)


class TestCompose:
    def test_default(self):
        c = compose_exam("cau_giay", date(2026, 11, 7), seed=1)
        assert len(c.questions) == 10
        assert c.answer_key

    def test_custom_blueprint(self):
        bp = {"total_questions": 5, "question_type_distribution": {"multiple_choice": 5}}
        c = compose_exam("cau_giay", date(2026, 11, 7), blueprint=bp, seed=2)
        assert len(c.questions) == 5
        assert all(q["type"] == "multiple_choice" for q in c.questions)

    def test_chuyen_de_weighting(self):
        bp = {"total_questions": 10, "chuyen_de_weights": {"hinh_hoc": 10.0}}
        c = compose_exam("cau_giay", date(2026, 11, 7), blueprint=bp, seed=3)
        hh = sum(1 for q in c.questions if q["chuyen_de"] == "hinh_hoc")
        assert hh >= 3

    def test_pad_when_type_dist_small(self):
        bp = {"total_questions": 10, "question_type_distribution": {"multiple_choice": 3}}
        c = compose_exam("cau_giay", date(2026, 11, 7), blueprint=bp, seed=4)
        assert len(c.questions) == 10
