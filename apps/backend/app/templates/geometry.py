"""Geometry templates."""

import random

from app.template_engine import TemplateError, TemplateSpec, register
from app.templates._helpers import build_mcq_choices, correct_letter


# ─── Diện tích HCN ────────────────────────────────────────────────
register(TemplateSpec(
    id="hinh_chu_nhat_dien_tich",
    chuyen_de="hinh_hoc",
    difficulty="NB",
    question_type="numeric",
    max_score=0.75,
    sampler=lambda rng: {"l": rng.randint(5, 20), "w": rng.randint(3, 15)},
    solver=lambda p: {"answer": p["l"] * p["w"]},
    content_builder=lambda p, s: f"Một hình chữ nhật có chiều dài {p['l']} m, rộng {p['w']} m. Tính diện tích.",
    steps_builder=lambda p, s: [{"desc": "S = d × r", "formula": f"{p['l']} × {p['w']} = {s['answer']}", "points": 0.75}],
    narrative_builder=lambda p, s: f"S = {p['l']} × {p['w']} = {s['answer']} m².",
    unit="m²",
))


# ─── Chu vi HCN (MCQ) ─────────────────────────────────────────────
def _peri_sampler(rng):
    return {"l": rng.randint(5, 25), "w": rng.randint(3, 20)}


def _peri_solver(p):
    peri = 2 * (p["l"] + p["w"])
    return {"answer_val": peri, "distractors": [p["l"] + p["w"], p["l"] * p["w"], 2 * p["l"] + p["w"]]}


def _peri_choices(p, s):
    rng = random.Random(p["l"] + p["w"])
    return build_mcq_choices(s["answer_val"], s["distractors"], rng)


register(TemplateSpec(
    id="hinh_chu_nhat_chu_vi",
    chuyen_de="hinh_hoc",
    difficulty="NB",
    question_type="multiple_choice",
    max_score=0.5,
    sampler=_peri_sampler,
    solver=lambda p: {**_peri_solver(p), "answer": correct_letter(_peri_choices(p, _peri_solver(p)), _peri_solver(p)["answer_val"])},
    content_builder=lambda p, s: f"Tính chu vi hình chữ nhật có chiều dài {p['l']} cm, chiều rộng {p['w']} cm.",
    choices_builder=lambda p, s: _peri_choices(p, _peri_solver(p)),
    steps_builder=lambda p, s: [{"desc": "P = 2 × (d + r)", "formula": f"2 × ({p['l']} + {p['w']}) = {_peri_solver(p)['answer_val']}", "points": 0.5}],
    narrative_builder=lambda p, s: f"Chu vi = 2 × ({p['l']} + {p['w']}) = {_peri_solver(p)['answer_val']} cm.",
))


# ─── Diện tích hình thang (tự luận) ───────────────────────────────
def _trap_sampler(rng):
    a = rng.choice([4, 6, 8])
    b = rng.choice([12, 14, 16])
    h = rng.choice([4, 6, 8])
    if ((a + b) * h) % 2 != 0:
        raise TemplateError("non-integer")
    return {"a": a, "b": b, "h": h}


def _trap_solver(p):
    sum_b = p["a"] + p["b"]
    area = sum_b * p["h"] // 2
    return {"answer": area, "sum_b": sum_b}


register(TemplateSpec(
    id="hinh_thang_dien_tich",
    chuyen_de="hinh_hoc",
    difficulty="TH",
    question_type="essay",
    max_score=1.0,
    sampler=_trap_sampler,
    solver=_trap_solver,
    content_builder=lambda p, s: (
        f"Một hình thang có đáy bé {p['a']} m, đáy lớn {p['b']} m, chiều cao {p['h']} m. "
        f"Trình bày lời giải tính diện tích hình thang."
    ),
    steps_builder=lambda p, s: [
        {"desc": "Tổng hai đáy", "formula": f"{p['a']} + {p['b']} = {s['sum_b']}", "points": 0.3},
        {"desc": "Diện tích", "formula": f"({s['sum_b']} × {p['h']}) ÷ 2 = {s['answer']}", "points": 0.7},
    ],
    narrative_builder=lambda p, s: f"Diện tích = ({p['a']} + {p['b']}) × {p['h']} ÷ 2 = {s['answer']} m².",
    unit="m²",
))
