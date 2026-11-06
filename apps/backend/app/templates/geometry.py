"""Geometry templates: hình chữ nhật, hình tam giác, hình thang, hình hộp."""

from __future__ import annotations

import random

from app.schemas import DifficultyLevel, QuestionType
from app.template_engine import TemplateError, TemplateSpec, register
from app.templates._helpers import build_mcq_choices, correct_letter


# ─── Template 10: Diện tích hình chữ nhật ──────────────────────────────
def _rect_area_sampler(rng: random.Random) -> dict:
    length = rng.randint(5, 20)
    width = rng.randint(3, length - 1)
    return {"length": length, "width": width}


def _rect_area_solver(p: dict) -> dict:
    area = p["length"] * p["width"]
    peri = 2 * (p["length"] + p["width"])
    return {"answer": area, "perimeter": peri}


def _rect_area_content(p: dict, s: dict) -> str:
    return f"Một hình chữ nhật có chiều dài {p['length']} m, chiều rộng {p['width']} m. Tính diện tích hình chữ nhật."


register(
    TemplateSpec(
        id="hinh_chu_nhat_dien_tich",
        chuyen_de="hinh_hoc",
        dang_bai="dien_tich_hcn",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.NUMERIC,
        max_score=0.75,
        sampler=_rect_area_sampler,
        solver=_rect_area_solver,
        content_builder=_rect_area_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Áp dụng công thức diện tích", "formula": f"{p['length']} × {p['width']} = {s['answer']}", "points": 0.75}
        ],
        narrative_builder=lambda p, s: f"Diện tích hình chữ nhật: {p['length']} × {p['width']} = {s['answer']} m².",
        unit="m²",
    )
)


# ─── Template 11: Chu vi hình chữ nhật ──────────────────────────────
def _rect_peri_sampler(rng: random.Random) -> dict:
    length = rng.randint(5, 25)
    width = rng.randint(3, length - 1)
    return {"length": length, "width": width}


def _rect_peri_solver(p: dict) -> dict:
    peri = 2 * (p["length"] + p["width"])
    distractors = [p["length"] + p["width"], p["length"] * p["width"], 2 * p["length"] + p["width"]]
    return {"answer": peri, "distractors": distractors}


def _rect_peri_content(p: dict, s: dict) -> str:
    return f"Một hình chữ nhật có chiều dài {p['length']} cm, chiều rộng {p['width']} cm. Tính chu vi."


def _rect_peri_choices(p: dict, s: dict) -> list:
    rng = random.Random(p["length"] + p["width"])
    return build_mcq_choices(s["answer"], s["distractors"], rng)


register(
    TemplateSpec(
        id="hinh_chu_nhat_chu_vi",
        chuyen_de="hinh_hoc",
        dang_bai="chu_vi_hcn",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.MULTIPLE_CHOICE,
        max_score=0.5,
        sampler=_rect_peri_sampler,
        solver=lambda p: {**_rect_peri_solver(p), "answer": correct_letter(_rect_peri_choices(p, _rect_peri_solver(p)), _rect_peri_solver(p)["answer"])},
        content_builder=_rect_peri_content,
        choices_builder=lambda p, s: _rect_peri_choices(p, _rect_peri_solver(p)),
        solution_steps_builder=lambda p, s: [{"desc": "Chu vi = 2 × (dài + rộng)", "formula": f"2 × ({p['length']} + {p['width']}) = {_rect_peri_solver(p)['answer']}", "points": 0.5}],
        narrative_builder=lambda p, s: f"Chu vi: 2 × ({p['length']} + {p['width']}) = {_rect_peri_solver(p)['answer']} cm.",
    )
)


# ─── Template 12: Diện tích hình tam giác ──────────────────────────────
def _tri_area_sampler(rng: random.Random) -> dict:
    base = rng.choice([4, 6, 8, 10, 12, 14, 16])
    height = rng.choice([3, 5, 7, 9, 11])
    return {"base": base, "height": height}


def _tri_area_solver(p: dict) -> dict:
    area_times_2 = p["base"] * p["height"]
    if area_times_2 % 2 != 0:
        raise TemplateError("non-integer area")
    area = area_times_2 // 2
    return {"answer": area}


def _tri_area_content(p: dict, s: dict) -> str:
    return f"Một hình tam giác có đáy {p['base']} cm, chiều cao {p['height']} cm. Tính diện tích tam giác."


register(
    TemplateSpec(
        id="hinh_tam_giac_dien_tich",
        chuyen_de="hinh_hoc",
        dang_bai="dien_tich_tam_giac",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=0.75,
        sampler=_tri_area_sampler,
        solver=_tri_area_solver,
        content_builder=_tri_area_content,
        solution_steps_builder=lambda p, s: [{"desc": "Áp dụng công thức", "formula": f"({p['base']} × {p['height']}) ÷ 2 = {s['answer']}", "points": 0.75}],
        narrative_builder=lambda p, s: f"Diện tích tam giác: ({p['base']} × {p['height']}) ÷ 2 = {s['answer']} cm².",
        unit="cm²",
    )
)


# ─── Template 13: Diện tích hình thang ──────────────────────────────
def _trap_sampler(rng: random.Random) -> dict:
    a = rng.choice([4, 6, 8, 10])
    b = rng.choice([12, 14, 16, 18])
    h = rng.choice([4, 6, 8, 10])
    return {"a": a, "b": b, "h": h}


def _trap_solver(p: dict) -> dict:
    area_times_2 = (p["a"] + p["b"]) * p["h"]
    if area_times_2 % 2 != 0:
        raise TemplateError("non-integer")
    return {"answer": area_times_2 // 2, "sum_bases": p["a"] + p["b"]}


def _trap_content(p: dict, s: dict) -> str:
    return (
        f"Một hình thang có đáy bé {p['a']} m, đáy lớn {p['b']} m, chiều cao {p['h']} m. "
        f"Tính diện tích hình thang."
    )


register(
    TemplateSpec(
        id="hinh_thang_dien_tich",
        chuyen_de="hinh_hoc",
        dang_bai="dien_tich_hinh_thang",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_trap_sampler,
        solver=_trap_solver,
        content_builder=_trap_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Tổng hai đáy", "formula": f"{p['a']} + {p['b']} = {s['sum_bases']}", "points": 0.3},
            {"desc": "Diện tích", "formula": f"({s['sum_bases']} × {p['h']}) ÷ 2 = {s['answer']}", "points": 0.7},
        ],
        narrative_builder=lambda p, s: f"Diện tích hình thang: ({p['a']} + {p['b']}) × {p['h']} ÷ 2 = {s['answer']} m².",
        unit="m²",
    )
)


# ─── Template 14: Thể tích hình hộp chữ nhật ──────────────────────────
def _box_sampler(rng: random.Random) -> dict:
    a = rng.randint(3, 10)
    b = rng.randint(3, 10)
    c = rng.randint(3, 10)
    return {"a": a, "b": b, "c": c}


def _box_solver(p: dict) -> dict:
    volume = p["a"] * p["b"] * p["c"]
    return {"answer": volume, "base_area": p["a"] * p["b"]}


def _box_content(p: dict, s: dict) -> str:
    return f"Một hình hộp chữ nhật có chiều dài {p['a']} cm, rộng {p['b']} cm, cao {p['c']} cm. Tính thể tích."


register(
    TemplateSpec(
        id="hinh_hop_cn_the_tich",
        chuyen_de="hinh_hoc",
        dang_bai="the_tich_hhcn",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=0.75,
        sampler=_box_sampler,
        solver=_box_solver,
        content_builder=_box_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Tích ba kích thước", "formula": f"{p['a']} × {p['b']} × {p['c']} = {s['answer']}", "points": 0.75}
        ],
        narrative_builder=lambda p, s: f"Thể tích: {p['a']} × {p['b']} × {p['c']} = {s['answer']} cm³.",
        unit="cm³",
    )
)


# ─── Template 15: Hình vuông — chu vi/diện tích ──────────────────────
def _square_sampler(rng: random.Random) -> dict:
    side = rng.randint(3, 20)
    return {"side": side}


def _square_solver(p: dict) -> dict:
    return {"answer": p["side"] * 4, "area": p["side"] ** 2}


register(
    TemplateSpec(
        id="hinh_vuong_chu_vi",
        chuyen_de="hinh_hoc",
        dang_bai="chu_vi_hv",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.NUMERIC,
        max_score=0.5,
        sampler=_square_sampler,
        solver=_square_solver,
        content_builder=lambda p, s: f"Tính chu vi hình vuông có cạnh {p['side']} cm.",
        solution_steps_builder=lambda p, s: [{"desc": "Chu vi = cạnh × 4", "formula": f"{p['side']} × 4 = {s['answer']}", "points": 0.5}],
        narrative_builder=lambda p, s: f"Chu vi hình vuông: {p['side']} × 4 = {s['answer']} cm.",
        unit="cm",
    )
)
