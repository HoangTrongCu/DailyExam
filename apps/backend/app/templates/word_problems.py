"""Word problem templates: tuổi, chuyển động, tỉ lệ."""

from app.template_engine import TemplateError, TemplateSpec, register


# ─── Bài toán tuổi ────────────────────────────────────────────────
def _age_sampler(rng):
    total = rng.randint(30, 80)
    diff = rng.randint(2, 20)
    if (total + diff) % 2 != 0:
        raise TemplateError("non-integer")
    father = (total + diff) // 2
    son = (total - diff) // 2
    if son < 5 or father < 25:
        raise TemplateError("unrealistic")
    return {"total": total, "diff": diff, "father": father, "son": son}


register(TemplateSpec(
    id="tuoi_tong_hieu",
    chuyen_de="bai_toan_tuoi",
    difficulty="TH",
    question_type="numeric",
    max_score=1.0,
    sampler=_age_sampler,
    solver=lambda p: {"answer": p["son"]},
    content_builder=lambda p, s: (
        f"Tổng số tuổi của hai bố con là {p['total']} tuổi. Bố hơn con {p['diff']} tuổi. "
        f"Tính tuổi của con."
    ),
    steps_builder=lambda p, s: [
        {"desc": "Tuổi bố", "formula": f"({p['total']} + {p['diff']}) ÷ 2 = {p['father']}", "points": 0.5},
        {"desc": "Tuổi con", "formula": f"{p['father']} - {p['diff']} = {p['son']}", "points": 0.5},
    ],
    narrative_builder=lambda p, s: f"Tuổi con: ({p['total']} - {p['diff']}) ÷ 2 = {p['son']} tuổi.",
    unit="tuổi",
))


# ─── Chuyển động ngược chiều ─────────────────────────────────────
def _motion_sampler(rng):
    v1 = rng.randint(30, 55)
    v2 = rng.randint(30, 55)
    d = (v1 + v2) * rng.randint(2, 4)
    return {"v1": v1, "v2": v2, "d": d}


def _motion_solver(p):
    tv = p["v1"] + p["v2"]
    t = p["d"] / tv
    if t != int(t):
        raise TemplateError("non-integer")
    return {"answer": int(t), "tv": tv}


register(TemplateSpec(
    id="chuyen_dong_nguoc_chieu",
    chuyen_de="chuyen_dong",
    difficulty="VD",
    question_type="numeric",
    max_score=1.0,
    sampler=_motion_sampler,
    solver=_motion_solver,
    content_builder=lambda p, s: (
        f"Hai xe xuất phát cùng lúc từ A và B cách nhau {p['d']} km, đi ngược chiều. "
        f"Vận tốc {p['v1']} km/h và {p['v2']} km/h. Hỏi sau bao nhiêu giờ hai xe gặp nhau?"
    ),
    steps_builder=lambda p, s: [
        {"desc": "Tổng vận tốc", "formula": f"{p['v1']} + {p['v2']} = {s['tv']}", "points": 0.4},
        {"desc": "Thời gian", "formula": f"{p['d']} ÷ {s['tv']} = {s['answer']}", "points": 0.6},
    ],
    narrative_builder=lambda p, s: f"Thời gian gặp nhau: {p['d']} ÷ {s['tv']} = {s['answer']} giờ.",
    unit="giờ",
))


# ─── Tỉ lệ thuận: mua hàng ────────────────────────────────────────
def _ratio_sampler(rng):
    a = rng.choice([2, 3, 4, 5])
    cost_a = rng.choice([5000, 8000, 10000, 12000, 15000])
    if cost_a % a != 0:
        raise TemplateError("non-integer")
    b = rng.randint(a + 1, a + 10)
    return {"a": a, "cost_a": cost_a, "b": b}


def _ratio_solver(p):
    unit = p["cost_a"] // p["a"]
    return {"answer": unit * p["b"], "unit": unit}


register(TemplateSpec(
    id="ti_le_thuan_mua_hang",
    chuyen_de="ti_le",
    difficulty="TH",
    question_type="numeric",
    max_score=0.75,
    sampler=_ratio_sampler,
    solver=_ratio_solver,
    content_builder=lambda p, s: f"Mua {p['a']} kg gạo hết {p['cost_a']:,} đồng. Hỏi mua {p['b']} kg gạo cùng loại hết bao nhiêu tiền?",
    steps_builder=lambda p, s: [
        {"desc": "Giá 1kg", "formula": f"{p['cost_a']} ÷ {p['a']} = {s['unit']}", "points": 0.4},
        {"desc": "Tổng tiền", "formula": f"{s['unit']} × {p['b']} = {s['answer']}", "points": 0.35},
    ],
    narrative_builder=lambda p, s: f"Tổng: {s['unit']} × {p['b']} = {s['answer']} đồng.",
    unit="đồng",
))
