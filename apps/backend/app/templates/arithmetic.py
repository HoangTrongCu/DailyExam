"""Arithmetic templates: trung bình cộng, tỉ số phần trăm, phân số."""

from __future__ import annotations

import random

from app.schemas import DifficultyLevel, QuestionType
from app.template_engine import TemplateError, TemplateSpec, register
from app.templates._helpers import build_mcq_choices, correct_letter, pick

# ─── Contexts ─────────────────────────────────────────────────────────────
PEOPLE = ["Bạn Nam", "Bạn An", "Bạn Hà", "Bạn Minh", "Bạn Mai", "Cô giáo"]
ITEMS_PLURAL = [
    {"name": "bài kiểm tra", "attr": "điểm", "unit": "điểm"},
    {"name": "quả cân", "attr": "khối lượng", "unit": "gam"},
    {"name": "túi gạo", "attr": "khối lượng", "unit": "kg"},
    {"name": "gói kẹo", "attr": "số viên", "unit": "viên"},
]


# ─── Template 1: Trung bình cộng — tìm số thiếu ─────────────────────────
def _tbc_sampler(rng: random.Random) -> dict:
    n = 3
    tbc = rng.randint(10, 50)
    s1 = rng.randint(5, 2 * tbc)
    s2 = rng.randint(5, 2 * tbc)
    s3 = tbc * n - s1 - s2
    if s3 <= 0 or s3 > 100:
        raise TemplateError("constraint: s3 out of range")
    ctx = pick(rng, ITEMS_PLURAL)
    person = pick(rng, PEOPLE)
    return {"n": n, "tbc": tbc, "s1": s1, "s2": s2, "person": person, "ctx": ctx}


def _tbc_solver(p: dict) -> dict:
    total = p["tbc"] * p["n"]
    s3 = total - p["s1"] - p["s2"]
    return {"answer": s3, "total": total, "sum_known": p["s1"] + p["s2"]}


def _tbc_content(p: dict, s: dict) -> str:
    c = p["ctx"]
    return (
        f"{p['person']} có {p['n']} {c['name']} với {c['attr']} trung bình là "
        f"{p['tbc']} {c['unit']}. {c['name'].capitalize()} thứ nhất có {c['attr']} "
        f"{p['s1']} {c['unit']}, {c['name']} thứ hai có {c['attr']} {p['s2']} {c['unit']}. "
        f"Hỏi {c['name']} thứ ba có {c['attr']} bao nhiêu {c['unit']}?"
    )


def _tbc_steps(p: dict, s: dict) -> list:
    c = p["ctx"]
    return [
        {"desc": f"Tính tổng {p['n']} {c['name']}", "formula": f"{p['tbc']} × {p['n']} = {s['total']}", "points": 0.4},
        {"desc": "Tính tổng 2 số đã biết", "formula": f"{p['s1']} + {p['s2']} = {s['sum_known']}", "points": 0.3},
        {"desc": f"Tính {c['name']} thứ ba", "formula": f"{s['total']} - {s['sum_known']} = {s['answer']}", "points": 0.3},
    ]


def _tbc_narrative(p: dict, s: dict) -> str:
    c = p["ctx"]
    return (
        f"Tổng của {p['n']} {c['name']} là: {p['tbc']} × {p['n']} = {s['total']} {c['unit']}.\n"
        f"Tổng của 2 {c['name']} đã biết là: {p['s1']} + {p['s2']} = {s['sum_known']} {c['unit']}.\n"
        f"Vậy {c['name']} thứ ba là: {s['total']} - {s['sum_known']} = {s['answer']} {c['unit']}."
    )


register(
    TemplateSpec(
        id="tbc_3so_tim_so_thieu",
        chuyen_de="trung_binh_cong",
        dang_bai="tim_so_thieu",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_tbc_sampler,
        solver=_tbc_solver,
        content_builder=_tbc_content,
        solution_steps_builder=_tbc_steps,
        narrative_builder=_tbc_narrative,
    )
)


# ─── Template 2: Trung bình cộng — MCQ ──────────────────────────────────
def _tbc_mcq_sampler(rng: random.Random) -> dict:
    n = rng.choice([3, 4, 5])
    nums = [rng.randint(5, 50) for _ in range(n)]
    total = sum(nums)
    if total % n != 0:
        raise TemplateError("tbc not integer")
    return {"n": n, "nums": nums}


def _tbc_mcq_solver(p: dict) -> dict:
    tbc = sum(p["nums"]) // p["n"]
    distractors = [tbc + 1, tbc - 1, sum(p["nums"]) // (p["n"] + 1)]
    return {"answer": tbc, "distractors": distractors, "total": sum(p["nums"])}


def _tbc_mcq_content(p: dict, s: dict) -> str:
    nums = ", ".join(str(n) for n in p["nums"])
    return f"Tính trung bình cộng của {p['n']} số sau: {nums}."


def _tbc_mcq_choices(p: dict, s: dict) -> list:
    rng = random.Random(sum(p["nums"]))
    return build_mcq_choices(s["answer"], s["distractors"], rng)


def _tbc_mcq_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Tính tổng các số", "formula": f"{' + '.join(str(n) for n in p['nums'])} = {s['total']}", "points": 0.5},
        {"desc": "Chia cho số lượng", "formula": f"{s['total']} ÷ {p['n']} = {s['answer']}", "points": 0.5},
    ]


def _tbc_mcq_narrative(p: dict, s: dict) -> str:
    return f"Tổng các số: {s['total']}. Trung bình cộng: {s['total']} ÷ {p['n']} = {s['answer']}."


def _tbc_mcq_correct(p: dict, s: dict) -> str:
    choices = _tbc_mcq_choices(p, s)
    return correct_letter(choices, s["answer"])


register(
    TemplateSpec(
        id="tbc_tinh_tbc_cua_n_so",
        chuyen_de="trung_binh_cong",
        dang_bai="tinh_tbc",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.MULTIPLE_CHOICE,
        max_score=0.75,
        sampler=_tbc_mcq_sampler,
        solver=lambda p: {**_tbc_mcq_solver(p), "answer": _tbc_mcq_correct(p, _tbc_mcq_solver(p))},
        content_builder=_tbc_mcq_content,
        choices_builder=lambda p, s: _tbc_mcq_choices(p, _tbc_mcq_solver(p)),
        solution_steps_builder=lambda p, s: _tbc_mcq_steps(p, _tbc_mcq_solver(p)),
        narrative_builder=lambda p, s: _tbc_mcq_narrative(p, _tbc_mcq_solver(p)),
    )
)


# ─── Template 3: Tỉ số phần trăm — tìm số lượng ─────────────────────────
def _pct_sampler(rng: random.Random) -> dict:
    total = rng.choice([200, 500, 800, 1000, 1200, 1500, 2000])
    pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
    count = total * pct // 100
    if count * 100 != total * pct:
        raise TemplateError("non-integer result")
    item = pick(rng, ["học sinh", "du khách", "sản phẩm", "cây trồng"])
    attribute = pick(rng, ["giỏi Toán", "thích phở", "đạt chuẩn", "ra hoa đúng vụ"])
    return {"total": total, "pct": pct, "item": item, "attribute": attribute}


def _pct_solver(p: dict) -> dict:
    count = p["total"] * p["pct"] // 100
    distractors = [count + p["total"] // 100, p["total"] - count, count * 2]
    return {"answer": count, "distractors": distractors}


def _pct_content(p: dict, s: dict) -> str:
    return (
        f"Trong {p['total']} {p['item']}, có {p['pct']}% {p['attribute']}. "
        f"Hỏi có bao nhiêu {p['item']} {p['attribute']}?"
    )


def _pct_choices(p: dict, s: dict) -> list:
    rng = random.Random(p["total"] + p["pct"])
    return build_mcq_choices(s["answer"], s["distractors"], rng)


def _pct_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Áp dụng công thức tìm phần trăm của một số", "formula": f"{p['total']} × {p['pct']} ÷ 100 = {s['answer']}", "points": 1.0},
    ]


def _pct_narrative(p: dict, s: dict) -> str:
    return f"Số {p['item']} {p['attribute']} là: {p['total']} × {p['pct']}% = {s['answer']} ({p['item']})."


register(
    TemplateSpec(
        id="phan_tram_tim_so_luong",
        chuyen_de="ti_so_phan_tram",
        dang_bai="tim_phan_tram_cua_so",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.MULTIPLE_CHOICE,
        max_score=0.75,
        sampler=_pct_sampler,
        solver=lambda p: {**_pct_solver(p), "answer": correct_letter(_pct_choices(p, _pct_solver(p)), _pct_solver(p)["answer"])},
        content_builder=_pct_content,
        choices_builder=lambda p, s: _pct_choices(p, _pct_solver(p)),
        solution_steps_builder=lambda p, s: _pct_steps(p, _pct_solver(p)),
        narrative_builder=lambda p, s: _pct_narrative(p, _pct_solver(p)),
    )
)


# ─── Template 4: Tỉ số phần trăm — tìm phần bù 100% ──────────────────────
def _pct_bu_sampler(rng: random.Random) -> dict:
    total = rng.choice([500, 1000, 1500, 2000])
    p1 = rng.randint(10, 35)
    p2 = rng.randint(10, 35)
    p3 = rng.randint(10, 35)
    rest = 100 - p1 - p2 - p3
    if rest <= 0 or rest > 50:
        raise TemplateError("rest out of range")
    rest_count = total * rest // 100
    if rest_count * 100 != total * rest:
        raise TemplateError("non-integer")
    items = pick(rng, [["phở", "bánh cuốn", "bún chả", "bánh mỳ"], ["cam", "táo", "nho", "xoài"]])
    return {"total": total, "p1": p1, "p2": p2, "p3": p3, "rest": rest, "items": items}


def _pct_bu_solver(p: dict) -> dict:
    rest_count = p["total"] * p["rest"] // 100
    distractors = [p["total"] - rest_count, rest_count + p["total"] // 100, p["total"] * (p["p1"] + p["p2"]) // 100]
    return {"answer": rest_count, "distractors": distractors, "rest_pct": p["rest"]}


def _pct_bu_content(p: dict, s: dict) -> str:
    items = p["items"]
    return (
        f"Có {p['total']} người được khảo sát món ăn ưa thích. {p['p1']}% thích {items[0]}, "
        f"{p['p2']}% thích {items[1]}, {p['p3']}% thích {items[2]}, còn lại thích {items[3]}. "
        f"Hỏi bao nhiêu người thích {items[3]}?"
    )


def _pct_bu_choices(p: dict, s: dict) -> list:
    rng = random.Random(p["total"] + p["p1"])
    return build_mcq_choices(s["answer"], s["distractors"], rng)


def _pct_bu_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Tính phần trăm còn lại", "formula": f"100% - {p['p1']}% - {p['p2']}% - {p['p3']}% = {s['rest_pct']}%", "points": 0.4},
        {"desc": "Tính số người thích món còn lại", "formula": f"{p['total']} × {s['rest_pct']}% = {s['answer']}", "points": 0.35},
    ]


def _pct_bu_narrative(p: dict, s: dict) -> str:
    return (
        f"Phần trăm còn lại: 100% - {p['p1']}% - {p['p2']}% - {p['p3']}% = {s['rest_pct']}%.\n"
        f"Số người thích {p['items'][3]}: {p['total']} × {s['rest_pct']}% = {s['answer']} người."
    )


register(
    TemplateSpec(
        id="phan_tram_tim_phan_bu",
        chuyen_de="ti_so_phan_tram",
        dang_bai="tim_phan_bu_100",
        difficulty=DifficultyLevel.VD,
        question_type=QuestionType.MULTIPLE_CHOICE,
        max_score=0.75,
        sampler=_pct_bu_sampler,
        solver=lambda p: {**_pct_bu_solver(p), "answer": correct_letter(_pct_bu_choices(p, _pct_bu_solver(p)), _pct_bu_solver(p)["answer"])},
        content_builder=_pct_bu_content,
        choices_builder=lambda p, s: _pct_bu_choices(p, _pct_bu_solver(p)),
        solution_steps_builder=lambda p, s: _pct_bu_steps(p, _pct_bu_solver(p)),
        narrative_builder=lambda p, s: _pct_bu_narrative(p, _pct_bu_solver(p)),
    )
)


# ─── Template 5: Phân số — cộng/trừ ────────────────────────────────────
def _phanso_sampler(rng: random.Random) -> dict:
    denom = rng.choice([4, 6, 8, 10, 12, 15])
    num1 = rng.randint(1, denom - 1)
    num2 = rng.randint(1, denom - 1)
    return {"num1": num1, "num2": num2, "denom": denom}


def _phanso_solver(p: dict) -> dict:
    sum_num = p["num1"] + p["num2"]
    import math
    g = math.gcd(sum_num, p["denom"])
    reduced = f"{sum_num // g}/{p['denom'] // g}" if g > 1 else f"{sum_num}/{p['denom']}"
    return {"answer": reduced, "sum_num": sum_num, "gcd": g}


def _phanso_content(p: dict, s: dict) -> str:
    return f"Tính: {p['num1']}/{p['denom']} + {p['num2']}/{p['denom']}. Rút gọn kết quả."


def _phanso_steps(p: dict, s: dict) -> list:
    return [
        {"desc": "Cộng tử số", "formula": f"({p['num1']} + {p['num2']})/{p['denom']} = {s['sum_num']}/{p['denom']}", "points": 0.5},
        {"desc": "Rút gọn", "formula": f"{s['sum_num']}/{p['denom']} = {s['answer']}", "points": 0.5},
    ]


register(
    TemplateSpec(
        id="phanso_cong_cung_mau",
        chuyen_de="phan_so",
        dang_bai="cong_phan_so",
        difficulty=DifficultyLevel.NB,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_phanso_sampler,
        solver=_phanso_solver,
        content_builder=_phanso_content,
        solution_steps_builder=_phanso_steps,
        narrative_builder=lambda p, s: f"{p['num1']}/{p['denom']} + {p['num2']}/{p['denom']} = {s['sum_num']}/{p['denom']} = {s['answer']}",
    )
)
