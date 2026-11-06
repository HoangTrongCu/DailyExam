"""School onboarding — framework for adding new schools via data.

Steps:
  1. collect: create workspace dir (manual: drop exam files in)
  2. analyze: parse past exams, extract style stats
  3. gen_config: write school_config.json from analysis
  4. gen_templates (future): synthesize school-specific templates
  5. verify: sanity-check config
  6. deploy: insert school + config into DB
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app import models

# ─── Keyword heuristics for pattern detection ─────────────────────────────
CHUYEN_DE_KEYWORDS = {
    "trung_binh_cong": ["trung bình cộng", "trung bình"],
    "ti_so_phan_tram": ["phần trăm", "%", "lãi", "giảm giá"],
    "bai_toan_tuoi": ["tuổi", "bố", "mẹ", "con"],
    "chuyen_dong": ["vận tốc", "quãng đường", "km/h", "ngược chiều", "cùng chiều", "gặp nhau"],
    "hinh_hoc": ["diện tích", "chu vi", "thể tích", "hình chữ nhật", "hình thang", "tam giác", "hình vuông", "hình tròn"],
    "phan_so": ["phân số", "tử số", "mẫu số"],
    "ti_le": ["tỉ lệ", "công nhân", "ngày"],
    "day_so": ["dãy số", "số hạng"],
    "dirichlet": ["chắc chắn", "ít nhất"],
    "cong_viec_chung": ["làm chung", "cùng làm"],
}


@dataclass
class AnalysisResult:
    total_questions: int
    chuyen_de_counts: dict[str, int]
    difficulty_dist: dict[str, float]


def analyze_exams(exam_text_blocks: list[str]) -> AnalysisResult:
    """Produce an AnalysisResult from raw text of past exams."""
    counts: Counter[str] = Counter()
    total = 0
    difficulty_hits: Counter[str] = Counter()

    for block in exam_text_blocks:
        text = block.lower()
        for topic, keywords in CHUYEN_DE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                counts[topic] += 1
                total += 1
        # Naive difficulty estimation by text length
        if len(block) < 150:
            difficulty_hits["NB"] += 1
        elif len(block) < 300:
            difficulty_hits["TH"] += 1
        elif len(block) < 500:
            difficulty_hits["VD"] += 1
        else:
            difficulty_hits["VDC"] += 1

    total_difficulty = sum(difficulty_hits.values()) or 1
    dist = {k: round(v / total_difficulty, 2) for k, v in difficulty_hits.items()}
    for level in ["NB", "TH", "VD", "VDC"]:
        dist.setdefault(level, 0.0)

    return AnalysisResult(total_questions=total, chuyen_de_counts=dict(counts), difficulty_dist=dist)


def generate_school_config(analysis: AnalysisResult, school_id: str, school_name: str) -> dict[str, Any]:
    """Convert analysis into a persistent school_config dict."""
    total_cd = sum(analysis.chuyen_de_counts.values()) or 1
    weights = {cd: round(count / total_cd, 3) for cd, count in analysis.chuyen_de_counts.items()}
    return {
        "school_id": school_id,
        "school_name": school_name,
        "num_questions": 10,
        "duration_minutes": 60,
        "difficulty_distribution": analysis.difficulty_dist
        or {"NB": 0.2, "TH": 0.3, "VD": 0.35, "VDC": 0.15},
        "chuyen_de_weights": weights,
        "style": {
            "co_bay_ratio": 0.3,
            "boi_canh_pool": ["truong_hoc", "mua_le", "ha_noi"],
            "tone": "formal",
        },
    }


def split_into_questions(text: str) -> list[str]:
    """Cheap splitter for exam text into question blocks."""
    import re
    pieces = re.split(r"(?:Bài|Câu|Question|B[àa]i)\s*\d+\s*[\.:]", text, flags=re.IGNORECASE)
    return [p.strip() for p in pieces if len(p.strip()) > 20]


def analyze_exam_files(file_paths: list[Path]) -> AnalysisResult:
    """Read .md/.txt exam files and analyze."""
    blocks: list[str] = []
    for fp in file_paths:
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8", errors="ignore")
        blocks.extend(split_into_questions(text))
    return analyze_exams(blocks)


def deploy_school(db: Session, school_id: str, school_name: str, config: dict[str, Any]) -> models.School:
    """Insert or update a school in the DB."""
    school = db.query(models.School).filter_by(id=school_id).first()
    if school:
        school.name = school_name
        school.config = config
    else:
        school = models.School(
            id=school_id,
            name=school_name,
            short_name=school_name,
            grade_levels=config.get("grade_levels", ["lop_5", "lop_6"]),
            config=config,
        )
        db.add(school)
    db.commit()
    db.refresh(school)
    return school


def save_config_to_disk(config: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
