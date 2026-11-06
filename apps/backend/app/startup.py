"""Seed the database on first startup with a default school and demo users."""

from __future__ import annotations

from app import models
from app.auth import hash_password
from app.db import get_session_factory


DEFAULT_CONFIG = {
    "school_id": "cau_giay",
    "school_name": "THCS Cầu Giấy",
    "num_questions": 10,
    "duration_minutes": 60,
    "difficulty_distribution": {"NB": 0.2, "TH": 0.3, "VD": 0.35, "VDC": 0.15},
    "chuyen_de_weights": {
        "trung_binh_cong": 0.15,
        "ti_so_phan_tram": 0.2,
        "hinh_hoc": 0.2,
        "bai_toan_tuoi": 0.1,
        "chuyen_dong": 0.15,
        "phan_so": 0.1,
        "ti_le": 0.05,
        "day_so": 0.03,
        "dirichlet": 0.02,
    },
    "style": {"tone": "formal", "boi_canh_pool": ["ha_noi", "truong_hoc"]},
}


def seed_initial_data() -> None:
    """Idempotent seed — creates school and demo users if absent."""
    factory = get_session_factory()
    with factory() as db:
        school = db.query(models.School).filter_by(id="cau_giay").first()
        if not school:
            school = models.School(
                id="cau_giay",
                name="THCS Cầu Giấy",
                short_name="Cầu Giấy",
                grade_levels=["lop_5", "lop_6"],
                config=DEFAULT_CONFIG,
            )
            db.add(school)

        demo_users = [
            ("hs@demo.vn", "Nguyễn Văn Nam", "student", "cau_giay"),
            ("admin@demo.vn", "Admin DailyExam", "admin", None),
        ]
        for email, name, role, school_id in demo_users:
            if not db.query(models.User).filter_by(email=email).first():
                db.add(
                    models.User(
                        email=email,
                        password_hash=hash_password("demo1234"),
                        full_name=name,
                        role=role,
                        status="active",
                        school_id=school_id,
                        grade="lop_5" if role == "student" else None,
                    )
                )
        db.commit()
