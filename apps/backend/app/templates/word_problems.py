"""Word problem templates: tuổi, chuyển động, công việc."""

from __future__ import annotations

import random

from app.schemas import DifficultyLevel, QuestionType
from app.template_engine import TemplateError, TemplateSpec, register
from app.templates._helpers import build_mcq_choices, correct_letter, pick


# ─── Template 6: Bài toán tuổi — tổng-hiệu ──────────────────────────────
def _age_sampler(rng: random.Random) -> dict:
    total = rng.randint(30, 80)
    diff = rng.randint(2, 20)
    if (total + diff) % 2 != 0:
        raise TemplateError("non-integer age")
    father = (total + diff) // 2
    son = (total - diff) // 2
    if son < 5 or father < 25:
        raise TemplateError("unrealistic ages")
    return {"total": total, "diff": diff, "father": father, "son": son}


def _age_solver(p: dict) -> dict:
    return {"answer": p["son"], "father": p["father"], "son": p["son"]}


def _age_content(p: dict, s: dict) -> str:
    return (
        f"Tổng số tuổi của hai bố con là {p['total']} tuổi. Bố hơn con {p['diff']} tuổi. "
        f"Tính tuổi của con."
    )


def _age_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Tuổi bố", "formula": f"({p['total']} + {p['diff']}) ÷ 2 = {p['father']}", "points": 0.5},
        {"desc": "Tuổi con", "formula": f"{p['father']} - {p['diff']} = {p['son']}", "points": 0.5},
    ]


register(
    TemplateSpec(
        id="tuoi_tong_hieu",
        chuyen_de="bai_toan_tuoi",
        dang_bai="tim_tuoi_bang_tong_hieu",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_age_sampler,
        solver=_age_solver,
        content_builder=_age_content,
        solution_steps_builder=_age_steps,
        narrative_builder=lambda p, s: f"Tuổi bố: ({p['total']} + {p['diff']}) ÷ 2 = {s['father']}. Tuổi con: {s['son']}.",
        unit="tuổi",
    )
)


# ─── Template 7: Chuyển động — ngược chiều ─────────────────────────────
def _motion_sampler(rng: random.Random) -> dict:
    v1 = rng.randint(30, 55)
    v2 = rng.randint(30, 55)
    distance = (v1 + v2) * rng.randint(2, 4)
    return {"v1": v1, "v2": v2, "distance": distance}


def _motion_solver(p: dict) -> dict:
    total_v = p["v1"] + p["v2"]
    time = p["distance"] / total_v
    if time != int(time):
        raise TemplateError("time not integer")
    return {"answer": int(time), "total_v": total_v}


def _motion_content(p: dict, s: dict) -> str:
    return (
        f"Hai xe xuất phát cùng lúc từ A và B cách nhau {p['distance']} km, đi ngược chiều nhau. "
        f"Xe từ A có vận tốc {p['v1']} km/h, xe từ B có vận tốc {p['v2']} km/h. "
        f"Hỏi sau bao nhiêu giờ hai xe gặp nhau?"
    )


def _motion_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Tổng vận tốc", "formula": f"{p['v1']} + {p['v2']} = {s['total_v']} km/h", "points": 0.5},
        {"desc": "Thời gian gặp nhau", "formula": f"{p['distance']} ÷ {s['total_v']} = {s['answer']} giờ", "points": 0.5},
    ]


register(
    TemplateSpec(
        id="chuyen_dong_nguoc_chieu",
        chuyen_de="chuyen_dong",
        dang_bai="hai_xe_nguoc_chieu",
        difficulty=DifficultyLevel.VD,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_motion_sampler,
        solver=_motion_solver,
        content_builder=_motion_content,
        solution_steps_builder=_motion_steps,
        narrative_builder=lambda p, s: f"Tổng vận tốc: {s['total_v']} km/h. Thời gian gặp nhau: {s['answer']} giờ.",
        unit="giờ",
    )
)


# ─── Template 8: Chuyển động — cùng chiều ─────────────────────────────
def _chase_sampler(rng: random.Random) -> dict:
    v_fast = rng.randint(50, 80)
    v_slow = rng.randint(20, 40)
    if v_fast <= v_slow:
        raise TemplateError("fast must be faster")
    head_start = (v_fast - v_slow) * rng.randint(2, 5)
    return {"v_fast": v_fast, "v_slow": v_slow, "head_start": head_start}


def _chase_solver(p: dict) -> dict:
    delta_v = p["v_fast"] - p["v_slow"]
    time = p["head_start"] / delta_v
    if time != int(time):
        raise TemplateError("non-integer")
    return {"answer": int(time), "delta_v": delta_v}


def _chase_content(p: dict, s: dict) -> str:
    return (
        f"Một xe máy đi với vận tốc {p['v_slow']} km/h. Sau đó {p['head_start']} km một ô tô đuổi theo "
        f"với vận tốc {p['v_fast']} km/h. Hỏi sau bao nhiêu giờ ô tô đuổi kịp xe máy?"
    )


def _chase_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Hiệu vận tốc", "formula": f"{p['v_fast']} - {p['v_slow']} = {s['delta_v']} km/h", "points": 0.5},
        {"desc": "Thời gian đuổi kịp", "formula": f"{p['head_start']} ÷ {s['delta_v']} = {s['answer']} giờ", "points": 0.5},
    ]


register(
    TemplateSpec(
        id="chuyen_dong_cung_chieu",
        chuyen_de="chuyen_dong",
        dang_bai="duoi_bat",
        difficulty=DifficultyLevel.VD,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_chase_sampler,
        solver=_chase_solver,
        content_builder=_chase_content,
        solution_steps_builder=_chase_steps,
        narrative_builder=lambda p, s: f"Hiệu vận tốc: {s['delta_v']} km/h. Thời gian đuổi kịp: {s['answer']} giờ.",
        unit="giờ",
    )
)


# ─── Template 9: Công việc — làm chung ──────────────────────────────────
def _work_sampler(rng: random.Random) -> dict:
    t1 = rng.choice([6, 8, 10, 12])
    t2 = rng.choice([4, 5, 6, 8])
    if t1 == t2:
        raise TemplateError("same times")
    return {"t1": t1, "t2": t2}


def _work_solver(p: dict) -> dict:
    # 1/t1 + 1/t2 = 1/t → t = t1*t2 / (t1+t2)
    from fractions import Fraction
    t = Fraction(p["t1"] * p["t2"], p["t1"] + p["t2"])
    if t.denominator == 1:
        return {"answer": int(t), "display": str(int(t))}
    return {"answer": str(t), "display": str(t)}


def _work_content(p: dict, s: dict) -> str:
    return (
        f"Người thứ nhất làm xong công việc trong {p['t1']} giờ. Người thứ hai làm xong công việc đó "
        f"trong {p['t2']} giờ. Hỏi cả hai người cùng làm thì sau bao nhiêu giờ xong công việc?"
    )


def _work_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Năng suất mỗi giờ", "formula": f"1/{p['t1']} + 1/{p['t2']}", "points": 0.5},
        {"desc": "Thời gian làm chung", "formula": f"({p['t1']} × {p['t2']}) ÷ ({p['t1']} + {p['t2']}) = {s['display']}", "points": 0.5},
    ]


register(
    TemplateSpec(
        id="cong_viec_lam_chung",
        chuyen_de="cong_viec_chung",
        dang_bai="hai_nguoi_lam_chung",
        difficulty=DifficultyLevel.VD,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_work_sampler,
        solver=_work_solver,
        content_builder=_work_content,
        solution_steps_builder=_work_steps,
        narrative_builder=lambda p, s: f"Thời gian làm chung: ({p['t1']} × {p['t2']}) ÷ ({p['t1']} + {p['t2']}) = {s['display']} giờ.",
        unit="giờ",
    )
)
