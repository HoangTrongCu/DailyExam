"""Tests for onboarding helpers."""

from pathlib import Path

import pytest

from app.onboarding import (
    analyze_exam_files,
    analyze_exams,
    generate_school_config,
    save_config_to_disk,
    split_into_questions,
)


SAMPLE_EXAM_TEXT = """
Bài 1. Tính trung bình cộng của ba số 10, 20 và 30.
Bài 2. Một hình chữ nhật có chiều dài 8 cm và chiều rộng 5 cm. Tính diện tích.
Bài 3. Một ô tô đi với vận tốc 60 km/h trong 2 giờ. Tính quãng đường.
Bài 4. Bố hơn con 25 tuổi. Tổng số tuổi của hai bố con là 45 tuổi. Tính tuổi của con.
"""


def test_split_into_questions() -> None:
    blocks = split_into_questions(SAMPLE_EXAM_TEXT)
    assert len(blocks) >= 3


def test_analyze_detects_topics() -> None:
    blocks = split_into_questions(SAMPLE_EXAM_TEXT)
    result = analyze_exams(blocks)
    assert "trung_binh_cong" in result.chuyen_de_counts
    assert "hinh_hoc" in result.chuyen_de_counts
    assert "chuyen_dong" in result.chuyen_de_counts


def test_generate_school_config() -> None:
    blocks = split_into_questions(SAMPLE_EXAM_TEXT)
    result = analyze_exams(blocks)
    config = generate_school_config(result, "test_school", "Test School")
    assert config["school_id"] == "test_school"
    assert config["num_questions"] == 10
    assert "chuyen_de_weights" in config
    # Difficulty distribution has all four levels
    for level in ["NB", "TH", "VD", "VDC"]:
        assert level in config["difficulty_distribution"]


def test_generate_config_empty_analysis() -> None:
    from app.onboarding import AnalysisResult
    empty = AnalysisResult(total_questions=0, chuyen_de_counts={}, difficulty_dist={})
    config = generate_school_config(empty, "x", "X")
    # Falls back to defaults
    assert config["difficulty_distribution"]["NB"] > 0


def test_analyze_exam_files(tmp_path: Path) -> None:
    f = tmp_path / "exam.md"
    f.write_text(SAMPLE_EXAM_TEXT, encoding="utf-8")
    result = analyze_exam_files([f, tmp_path / "missing.md"])
    assert result.total_questions > 0


def test_save_config_to_disk(tmp_path: Path) -> None:
    config = {"a": 1}
    out = tmp_path / "nested" / "config.json"
    save_config_to_disk(config, out)
    assert out.exists()
    import json
    assert json.loads(out.read_text(encoding="utf-8")) == config


def test_cli_onboard_runs(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("DAILYEXAM_DATABASE_URL", f"sqlite:///{db_path}")
    import app.db as db_module
    db_module._engine = None
    db_module._SessionLocal = None

    exams_dir = tmp_path / "raw"
    exams_dir.mkdir()
    (exams_dir / "e.md").write_text(SAMPLE_EXAM_TEXT, encoding="utf-8")

    from app.cli_onboard import main
    rc = main([
        "demo_school",
        "--name",
        "Demo",
        "--exams-dir",
        str(exams_dir),
        "--output-dir",
        str(tmp_path / "out"),
    ])
    assert rc == 0
    assert (tmp_path / "out" / "demo_school" / "config" / "school_config.json").exists()
