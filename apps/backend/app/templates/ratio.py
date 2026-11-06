"""Ratio templates: tỉ lệ, dãy số, Dirichlet."""

from __future__ import annotations

import random

from app.schemas import DifficultyLevel, QuestionType
from app.template_engine import TemplateError, TemplateSpec, register


# ─── Template 16: Tỉ lệ thuận ──────────────────────────────────────────
def _tl_thuan_sampler(rng: random.Random) -> dict:
    a = rng.choice([2, 3, 4, 5])
    cost_per_a = rng.choice([5000, 8000, 10000, 12000, 15000, 20000])
    b = rng.randint(a + 1, a + 10)
    return {"a": a, "cost_per_a": cost_per_a, "b": b}


def _tl_thuan_solver(p: dict) -> dict:
    unit = p["cost_per_a"] / p["a"]
    if unit != int(unit):
        raise TemplateError("non-integer unit")
    total = int(unit) * p["b"]
    return {"answer": total, "unit": int(unit)}


def _tl_thuan_content(p: dict, s: dict) -> str:
    return (
        f"Mua {p['a']} kg gạo hết {p['cost_per_a']:,} đồng. Hỏi mua {p['b']} kg gạo cùng loại "
        f"hết bao nhiêu tiền?"
    )


register(
    TemplateSpec(
        id="ti_le_thuan_kg_gao",
        chuyen_de="ti_le",
        dang_bai="ti_le_thuan",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=0.75,
        sampler=_tl_thuan_sampler,
        solver=_tl_thuan_solver,
        content_builder=_tl_thuan_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Giá 1 kg", "formula": f"{p['cost_per_a']} ÷ {p['a']} = {s['unit']}", "points": 0.4},
            {"desc": "Tổng tiền", "formula": f"{s['unit']} × {p['b']} = {s['answer']}", "points": 0.35},
        ],
        narrative_builder=lambda p, s: f"Giá 1kg: {s['unit']} đồng. Tổng: {s['answer']:,} đồng.",
        unit="đồng",
    )
)


# ─── Template 17: Tỉ lệ nghịch ──────────────────────────────────────────
def _tl_nghich_sampler(rng: random.Random) -> dict:
    workers1 = rng.choice([4, 5, 6, 8])
    days1 = rng.choice([6, 8, 10, 12])
    workers2 = rng.randint(workers1 + 1, workers1 + 8)
    return {"w1": workers1, "d1": days1, "w2": workers2}


def _tl_nghich_solver(p: dict) -> dict:
    total_work = p["w1"] * p["d1"]
    days2 = total_work / p["w2"]
    if days2 != int(days2):
        raise TemplateError("non-integer")
    return {"answer": int(days2), "total_work": total_work}


def _tl_nghich_content(p: dict, s: dict) -> str:
    return (
        f"{p['w1']} công nhân làm xong một việc trong {p['d1']} ngày. "
        f"Hỏi {p['w2']} công nhân (có cùng năng suất) làm xong việc đó trong bao nhiêu ngày?"
    )


register(
    TemplateSpec(
        id="ti_le_nghich_cong_nhan",
        chuyen_de="ti_le",
        dang_bai="ti_le_nghich",
        difficulty=DifficultyLevel.TH,
        question_type=QuestionType.NUMERIC,
        max_score=0.75,
        sampler=_tl_nghich_sampler,
        solver=_tl_nghich_solver,
        content_builder=_tl_nghich_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Tổng công việc (công × ngày)", "formula": f"{p['w1']} × {p['d1']} = {s['total_work']}", "points": 0.4},
            {"desc": "Số ngày", "formula": f"{s['total_work']} ÷ {p['w2']} = {s['answer']}", "points": 0.35},
        ],
        narrative_builder=lambda p, s: f"Tổng công: {s['total_work']} công. Số ngày: {s['answer']} ngày.",
        unit="ngày",
    )
)


# ─── Template 18: Dãy số cách đều — số hạng thứ n ──────────────────────
def _seq_sampler(rng: random.Random) -> dict:
    first = rng.randint(1, 10)
    diff = rng.randint(2, 5)
    n = rng.randint(10, 50)
    return {"first": first, "diff": diff, "n": n}


def _seq_solver(p: dict) -> dict:
    nth = p["first"] + (p["n"] - 1) * p["diff"]
    return {"answer": nth}


register(
    TemplateSpec(
        id="day_so_cach_deu_so_hang_n",
        chuyen_de="day_so",
        dang_bai="tim_so_hang_thu_n",
        difficulty=DifficultyLevel.VD,
        question_type=QuestionType.NUMERIC,
        max_score=1.0,
        sampler=_seq_sampler,
        solver=_seq_solver,
        content_builder=lambda p, s: f"Cho dãy số: {p['first']}, {p['first']+p['diff']}, {p['first']+2*p['diff']}, ... (mỗi số hơn số liền trước {p['diff']} đơn vị). Hỏi số hạng thứ {p['n']} của dãy là bao nhiêu?",
        solution_steps_builder=lambda p, s: [
            {"desc": "Công thức số hạng tổng quát", "formula": f"a_n = a_1 + (n - 1) × d = {p['first']} + ({p['n']} - 1) × {p['diff']} = {s['answer']}", "points": 1.0}
        ],
        narrative_builder=lambda p, s: f"Số hạng thứ {p['n']}: {p['first']} + ({p['n']}-1) × {p['diff']} = {s['answer']}.",
    )
)


# ─── Template 19: Dãy số cách đều — tổng ────────────────────────────────
def _seq_sum_sampler(rng: random.Random) -> dict:
    first = rng.randint(1, 5)
    diff = rng.choice([1, 2, 3])
    n = rng.choice([10, 20, 50, 100])
    return {"first": first, "diff": diff, "n": n}


def _seq_sum_solver(p: dict) -> dict:
    last = p["first"] + (p["n"] - 1) * p["diff"]
    total = (p["first"] + last) * p["n"] // 2
    return {"answer": total, "last": last}


register(
    TemplateSpec(
        id="day_so_tinh_tong",
        chuyen_de="day_so",
        dang_bai="tong_day_cach_deu",
        difficulty=DifficultyLevel.VDC,
        question_type=QuestionType.NUMERIC,
        max_score=1.5,
        sampler=_seq_sum_sampler,
        solver=_seq_sum_solver,
        content_builder=lambda p, s: f"Tính tổng {p['n']} số hạng đầu tiên của dãy: {p['first']}, {p['first']+p['diff']}, {p['first']+2*p['diff']}, ... (hiệu giữa hai số liền nhau là {p['diff']}).",
        solution_steps_builder=lambda p, s: [
            {"desc": "Tìm số hạng cuối", "formula": f"a_n = {p['first']} + ({p['n']}-1) × {p['diff']} = {s['last']}", "points": 0.5},
            {"desc": "Áp dụng công thức tổng", "formula": f"S = ({p['first']} + {s['last']}) × {p['n']} ÷ 2 = {s['answer']}", "points": 1.0},
        ],
        narrative_builder=lambda p, s: f"Số hạng cuối: {s['last']}. Tổng: ({p['first']} + {s['last']}) × {p['n']} ÷ 2 = {s['answer']}.",
    )
)


# ─── Template 20: Dirichlet — chọn bi ────────────────────────────────────
def _dirichlet_sampler(rng: random.Random) -> dict:
    red = rng.randint(5, 15)
    blue = rng.randint(5, 15)
    green = rng.randint(5, 15)
    return {"red": red, "blue": blue, "green": green}


def _dirichlet_solver(p: dict) -> dict:
    # Lấy ít nhất bao nhiêu viên để chắc chắn có 3 viên cùng màu?
    # Trường hợp xấu nhất: 2 viên mỗi màu (6 viên) → viên thứ 7 sẽ cùng màu với 1 trong 3 cặp
    answer = 2 * 3 + 1
    return {"answer": answer}


def _dirichlet_content(p: dict, s: dict) -> str:
    return (
        f"Trong hộp có {p['red']} viên bi đỏ, {p['blue']} viên bi xanh, {p['green']} viên bi vàng. "
        f"Nhắm mắt lấy ngẫu nhiên, hỏi cần lấy ít nhất bao nhiêu viên bi để chắc chắn có "
        f"ít nhất 3 viên bi cùng màu?"
    )


register(
    TemplateSpec(
        id="dirichlet_3_vien_cung_mau",
        chuyen_de="dirichlet",
        dang_bai="chon_vat_cung_loai",
        difficulty=DifficultyLevel.VDC,
        question_type=QuestionType.NUMERIC,
        max_score=1.5,
        sampler=_dirichlet_sampler,
        solver=_dirichlet_solver,
        content_builder=_dirichlet_content,
        solution_steps_builder=lambda p, s: [
            {"desc": "Trường hợp xấu nhất", "formula": "Mỗi màu lấy được tối đa 2 viên khác → 2 × 3 = 6 viên", "points": 0.75},
            {"desc": "Thêm 1 viên nữa chắc chắn thành 3 cùng màu", "formula": "6 + 1 = 7", "points": 0.75},
        ],
        narrative_builder=lambda p, s: f"Theo nguyên lí Dirichlet: cần {s['answer']} viên để chắc chắn có 3 viên cùng màu.",
        unit="viên",
    )
)
