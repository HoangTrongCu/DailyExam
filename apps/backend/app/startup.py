"""Seed initial data (idempotent)."""

from datetime import datetime, timezone

from app import models
from app.auth import hash_password
from app.db import get_session_factory

CAU_GIAY_BLUEPRINT = {
    "exam_duration_minutes": 60,
    "total_questions": 10,
    "difficulty_distribution": {"NB": 0.2, "TH": 0.3, "VD": 0.35, "VDC": 0.15},
    "question_type_distribution": {"multiple_choice": 5, "numeric": 3, "essay": 2},
    "chuyen_de_weights": {
        "trung_binh_cong": 0.15,
        "ti_so_phan_tram": 0.2,
        "hinh_hoc": 0.2,
        "bai_toan_tuoi": 0.1,
        "chuyen_dong": 0.15,
        "phan_so": 0.1,
        "ti_le": 0.1,
    },
}


def seed() -> None:
    factory = get_session_factory()
    with factory() as db:
        if not db.query(models.School).filter_by(id="cau_giay").first():
            db.add(models.School(id="cau_giay", name="THCS Cầu Giấy", short_name="Cầu Giấy"))
        if not db.query(models.Blueprint).filter_by(school_id="cau_giay", is_active=True).first():
            db.add(models.Blueprint(school_id="cau_giay", version=1, structure=CAU_GIAY_BLUEPRINT))
        if not db.query(models.User).filter_by(email="hs@demo.vn").first():
            db.add(models.User(
                email="hs@demo.vn",
                password_hash=hash_password("demo1234"),
                full_name="Phụ huynh Nam",
                child_name="Nguyễn Văn Nam",
                role="student",
                status="active",
                email_verified_at=datetime.now(timezone.utc),
            ))
        if not db.query(models.User).filter_by(email="admin@demo.vn").first():
            db.add(models.User(
                email="admin@demo.vn",
                password_hash=hash_password("demo1234"),
                full_name="Admin DailyExam",
                role="admin",
                status="active",
                email_verified_at=datetime.now(timezone.utc),
            ))
        db.commit()
