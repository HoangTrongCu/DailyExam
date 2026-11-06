"""CLI: python -m app.cli_onboard <school_slug> [--name "..."] [--exams-dir ...]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.db import get_session_factory, init_db
from app.onboarding import (
    analyze_exam_files,
    deploy_school,
    generate_school_config,
    save_config_to_disk,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Onboard a school into DailyExam")
    parser.add_argument("school_slug", help="Short identifier (e.g. cau_giay)")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--exams-dir", type=Path, default=None, help="Dir with .md/.txt past exams")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("schools"),
        help="Where to write school_config.json",
    )
    args = parser.parse_args(argv)

    init_db()

    exam_files: list[Path] = []
    if args.exams_dir and args.exams_dir.exists():
        exam_files = sorted(args.exams_dir.glob("*.md")) + sorted(args.exams_dir.glob("*.txt"))

    analysis = analyze_exam_files(exam_files)
    config = generate_school_config(analysis, args.school_slug, args.name)

    output = args.output_dir / args.school_slug / "config"
    save_config_to_disk(config, output / "school_config.json")

    factory = get_session_factory()
    with factory() as db:
        school = deploy_school(db, args.school_slug, args.name, config)

    print(json.dumps({
        "school_id": school.id,
        "config_path": str(output / "school_config.json"),
        "analysis": {
            "questions_detected": analysis.total_questions,
            "chuyen_de_counts": analysis.chuyen_de_counts,
            "difficulty_dist": analysis.difficulty_dist,
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
