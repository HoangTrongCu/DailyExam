"""Arithmetic templates."""

import random
from math import gcd

from app.template_engine import TemplateError, TemplateSpec, register
from app.templates._helpers import build_mcq_choices, correct_letter, pick


ITEMS = [
    {"name": "bài kiểm tra", "attr": "điểm", "unit": "điểm"},
    {"name": "quả cân", "attr": "khối lượng", "unit": "g"},
    {"name": "túi gạo", "attr": "khối lượng", "unit": "kg"},
]
PEOPLE = ["Bạn Nam", "Bạn An", "Bạn Hà", "Bạn Minh"]


# ─── Template 1: TBC 3 số, tìm số thiếu ───────────────────────────
def _tbc_sampler(rng):
    tbc = rng.randint(10, 50)
    s1 = rng.randint(5, 2 * tbc)
    s2 = rng.randint(5, 2 * tbc)
    s3 = tbc * 3 - s1 - s2
    if not (0 < s3 <= 100):
        raise TemplateError("out of range")
    return {"tbc": tbc, "s1": s1, "s2": s2, "person": pick(rng, PEOPLE), "ctx": pick(rng, ITEMS)}


def _tbc_solver(p):
    total = p["tbc"] * 3
    s3 = total - p["s1"] - p["s2"]
    return {"answer": s3, "total": total, "sum_known": p["s1"] + p["s2"]}


def _tbc_content(p, s):
    c = p["ctx"]
    return (
        f"{p['person']} có 3 {c['name']} với {c['attr']} trung bình là "
        f"{p['tbc']} {c['unit']}. Hai {c['name']} đầu có {c['attr']} "
        f"{p['s1']} {c['unit']} và {p['s2']} {c['unit']}. "
        f"Hỏi {c['name']} còn lại có {c['attr']} bao nhiêu?"
    )


register(TemplateSpec(
    id="tbc_tim_so_thieu",
    chuyen_de="trung_binh_cong",
    difficulty="TH",
    question_type="numeric",
    max_score=1.0,
    sampler=_tbc_sampler,
    solver=_tbc_solver,
    content_builder=_tbc_content,
    steps_builder=lambda p, s: [
        {"desc": "Tính tổng 3 số", "formula": f"{p['tbc']} × 3 = {s['total']}", "points": 0.4},
        {"desc": "Tổng 2 số đã biết", "formula": f"{p['s1']} + {p['s2']} = {s['sum_known']}", "points": 0.3},
        {"desc": "Số còn lại", "formula": f"{s['total']} - {s['sum_known']} = {s['answer']}", "points": 0.3},
    ],
    narrative_builder=lambda p, s: f"Số còn lại = {s['total']} - {s['sum_known']} = {s['answer']}.",
    unit="đơn vị",
))


# ─── Template 2: TBC MCQ — tính TBC của n số ──────────────────────
def _tbc_mcq_sampler(rng):
    n = rng.choice([3, 4, 5])
    nums = [rng.randint(5, 50) for _ in range(n)]
    if sum(nums) % n != 0:
        raise TemplateError("non-integer tbc")
    return {"n": n, "nums": nums}


def _tbc_mcq_solver(p):
    tbc = sum(p["nums"]) // p["n"]
    return {"answer_val": tbc, "distractors": [tbc + 1, tbc - 1, tbc * 2]}


def _tbc_mcq_choices(p, s):
    rng = random.Random(sum(p["nums"]))
    return build_mcq_choices(s["answer_val"], s["distractors"], rng)


register(TemplateSpec(
    id="tbc_tinh_cua_n_so",
    chuyen_de="trung_binh_cong",
    difficulty="NB",
    question_type="multiple_choice",
    max_score=0.75,
    sampler=_tbc_mcq_sampler,
    solver=lambda p: {**_tbc_mcq_solver(p), "answer": correct_letter(_tbc_mcq_choices(p, _tbc_mcq_solver(p)), _tbc_mcq_solver(p)["answer_val"])},
    content_builder=lambda p, s: f"Tính trung bình cộng của {p['n']} số: {', '.join(str(n) for n in p['nums'])}.",
    choices_builder=lambda p, s: _tbc_mcq_choices(p, _tbc_mcq_solver(p)),
    steps_builder=lambda p, s: [
        {"desc": "Tổng các số", "formula": f"{' + '.join(str(n) for n in p['nums'])} = {sum(p['nums'])}", "points": 0.5},
        {"desc": "Chia cho số lượng", "formula": f"{sum(p['nums'])} ÷ {p['n']} = {sum(p['nums']) // p['n']}", "points": 0.25},
    ],
    narrative_builder=lambda p, s: f"TBC = {sum(p['nums'])} ÷ {p['n']} = {sum(p['nums']) // p['n']}.",
))


# ─── Template 3: Phần trăm — tìm số lượng ─────────────────────────
def _pct_sampler(rng):
    total = rng.choice([200, 500, 1000, 1500, 2000])
    pct = rng.choice([10, 15, 20, 25, 30, 40, 50])
    cnt = total * pct // 100
    if cnt * 100 != total * pct:
        raise TemplateError("non-integer")
    item = pick(rng, ["học sinh", "du khách", "sản phẩm"])
    attr = pick(rng, ["đạt chuẩn", "giỏi toán", "thích phở"])
    return {"total": total, "pct": pct, "item": item, "attr": attr}


def _pct_solver(p):
    cnt = p["total"] * p["pct"] // 100
    return {"answer_val": cnt, "distractors": [cnt + p["total"] // 100, p["total"] - cnt, cnt * 2]}


def _pct_choices(p, s):
    rng = random.Random(p["total"] + p["pct"])
    return build_mcq_choices(s["answer_val"], s["distractors"], rng)


register(TemplateSpec(
    id="phan_tram_tim_so_luong",
    chuyen_de="ti_so_phan_tram",
    difficulty="TH",
    question_type="multiple_choice",
    max_score=0.75,
    sampler=_pct_sampler,
    solver=lambda p: {**_pct_solver(p), "answer": correct_letter(_pct_choices(p, _pct_solver(p)), _pct_solver(p)["answer_val"])},
    content_builder=lambda p, s: f"Trong {p['total']} {p['item']}, có {p['pct']}% {p['attr']}. Hỏi có bao nhiêu {p['item']} {p['attr']}?",
    choices_builder=lambda p, s: _pct_choices(p, _pct_solver(p)),
    steps_builder=lambda p, s: [
        {"desc": "Áp dụng công thức phần trăm", "formula": f"{p['total']} × {p['pct']} ÷ 100 = {_pct_solver(p)['answer_val']}", "points": 0.75}
    ],
    narrative_builder=lambda p, s: f"Số {p['item']} {p['attr']}: {p['total']} × {p['pct']}% = {_pct_solver(p)['answer_val']}.",
))


# ─── Template 4: Phần trăm — tự luận với lý do ─────────────────────
def _pct_essay_sampler(rng):
    total = rng.choice([800, 1000, 1500, 2000])
    p1 = rng.randint(15, 35)
    p2 = rng.randint(15, 35)
    rest_pct = 100 - p1 - p2
    if not (10 <= rest_pct <= 50):
        raise TemplateError("rest out of range")
    rest_cnt = total * rest_pct // 100
    if rest_cnt * 100 != total * rest_pct:
        raise TemplateError("non-integer")
    return {"total": total, "p1": p1, "p2": p2, "rest_pct": rest_pct, "items": ["phở", "bún chả", "bánh cuốn"]}


def _pct_essay_solver(p):
    cnt = p["total"] * p["rest_pct"] // 100
    return {"answer": cnt}


register(TemplateSpec(
    id="phan_tram_tu_luan",
    chuyen_de="ti_so_phan_tram",
    difficulty="VD",
    question_type="essay",
    max_score=1.5,
    sampler=_pct_essay_sampler,
    solver=_pct_essay_solver,
    content_builder=lambda p, s: (
        f"Có {p['total']} người được khảo sát món ăn ưa thích. "
        f"{p['p1']}% thích {p['items'][0]}, {p['p2']}% thích {p['items'][1]}, còn lại thích {p['items'][2]}. "
        f"Trình bày lời giải tìm số người thích {p['items'][2]}."
    ),
    steps_builder=lambda p, s: [
        {"desc": "Tính phần trăm còn lại", "formula": f"100% - {p['p1']}% - {p['p2']}% = {p['rest_pct']}%", "points": 0.5},
        {"desc": "Tính số người thích món còn lại", "formula": f"{p['total']} × {p['rest_pct']}% = {s['answer']}", "points": 1.0},
    ],
    narrative_builder=lambda p, s: (
        f"Phần trăm còn lại: 100% - {p['p1']}% - {p['p2']}% = {p['rest_pct']}%.\n"
        f"Số người thích {p['items'][2]}: {p['total']} × {p['rest_pct']}% = {s['answer']} người."
    ),
    unit="người",
))


# ─── Template 5: Phân số — cộng cùng mẫu ─────────────────────────
def _phanso_sampler(rng):
    d = rng.choice([4, 6, 8, 10, 12])
    n1, n2 = rng.randint(1, d - 1), rng.randint(1, d - 1)
    return {"n1": n1, "n2": n2, "d": d}


def _phanso_solver(p):
    s = p["n1"] + p["n2"]
    g = gcd(s, p["d"])
    reduced = f"{s // g}/{p['d'] // g}" if g > 1 else f"{s}/{p['d']}"
    return {"answer": reduced, "sum": s, "gcd": g}


register(TemplateSpec(
    id="phanso_cong_cung_mau",
    chuyen_de="phan_so",
    difficulty="NB",
    question_type="numeric",
    max_score=0.75,
    sampler=_phanso_sampler,
    solver=_phanso_solver,
    content_builder=lambda p, s: f"Tính và rút gọn: {p['n1']}/{p['d']} + {p['n2']}/{p['d']}.",
    steps_builder=lambda p, s: [
        {"desc": "Cộng tử số", "formula": f"({p['n1']} + {p['n2']})/{p['d']} = {s['sum']}/{p['d']}", "points": 0.4},
        {"desc": "Rút gọn (nếu có)", "formula": f"{s['sum']}/{p['d']} = {s['answer']}", "points": 0.35},
    ],
    narrative_builder=lambda p, s: f"{p['n1']}/{p['d']} + {p['n2']}/{p['d']} = {s['answer']}.",
))
