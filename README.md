# DailyExam

AI-powered daily exam platform for VN secondary school entrance prep.

- **Subject (MVP)**: Toán · Lớp 5 · Thi vào lớp 6 CLC
- **Pilot school**: THCS Cầu Giấy
- **Style**: Claymorphism · Gamified Edu (amber + green palette)

## Docs
- [SRS (Software Requirements Spec)](docs/SRS.md)
- [SDD (System Design Doc)](docs/SDD.md)

## Quick Start

```bash
# Clone
git clone https://github.com/HoangTrongCu/DailyExam.git
cd DailyExam

# Dev with Docker
docker compose up --build

# Local backend
cd apps/backend
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/uvicorn app.main:app --reload

# Local frontend
cd apps/web
npm install
npm test
npm run dev
```

URLs (via docker-compose):
- Web: http://localhost:3001
- Backend API: http://localhost:8001
- API docs: http://localhost:8001/docs

Demo accounts (seeded):
- HS: `hs@demo.vn` / `demo1234`
- Admin: `admin@demo.vn` / `demo1234`

## Quality Gates
- Backend coverage ≥85%
- Frontend coverage ≥85%
- Code duplication <2.5%

## License
Private — do not redistribute.
