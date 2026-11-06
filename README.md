# DailyExam

AI-powered daily exam platform — tự động sinh đề và chấm bài mỗi ngày cho các trường THCS/Tiểu học.

**Pilot subject**: Toán (Math)
**Pilot school**: THCS Cầu Giấy
**Target launch**: Q1 2027

## Core Concept

- **1 trường / 1 ngày / 1 đề** dùng chung cho toàn trường
- **Auto-generate** lúc 5h sáng, mở cổng 8h, đóng 9h, release kết quả 9h30
- **Reference-based grading**: Lời giải chuẩn sinh cùng đề → chấm tự luận chính xác >90%
- **Multi-tenant**: Thêm trường mới chỉ cần data, không sửa code
- **Multi-subject ready**: Kiến trúc mở rộng sang Văn, Anh, Lý, Hóa...

## Architecture

- **Backend**: Python 3.12 + FastAPI
- **Math engine**: SymPy
- **LLM**: Claude Haiku 4.5 (primary) + Sonnet 4.6 (escalation)
- **Database**: PostgreSQL + Redis
- **Frontend**: Next.js 15 + TypeScript + shadcn/ui + KaTeX
- **Queue**: Celery + Redis

## Status

🚧 **In planning** — Phase 0 (foundation setup).

See `docs/plans/` for the master plan.

## Repository Structure

```
DailyExam/
├── engine/              # Generic engine (shared across subjects/schools)
├── core_templates/      # Math core templates (100)
├── schools/             # Per-school data (config + templates)
│   └── cau_giay/
├── subjects/            # Subject-specific modules (math, literature, ...)
│   └── math/
├── onboarding/          # School onboarding CLI
├── schemas/             # JSON schemas
├── apps/
│   ├── web/             # Student + teacher portal
│   └── admin/           # Admin panel
├── docs/
│   └── plans/           # Master plans and architecture docs
└── tests/
```

## License

Private.
