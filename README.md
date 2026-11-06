# DailyExam

AI-powered daily exam platform — **mỗi ngày 1 đề**, **chấm bài tự động** cho học sinh tiểu học và THCS.

- **Pilot subject**: Toán (Math)
- **Pilot school**: THCS Cầu Giấy
- **Status**: Foundation / Phase 1 (skeleton ready)

## Design System

- **Style**: Claymorphism (soft, playful, student-friendly)
- **Palette**: Learning blue `#2563EB` + Play yellow `#F59E0B` + Fun pink `#EC4899`
- **Fonts**: `Baloo 2` (headings) + `Comic Neue` (body)
- **Token source of truth**: `packages/design-tokens/tokens.json` + `tokens.css`

## Repository Structure

```
DailyExam/
├── apps/
│   ├── backend/              # FastAPI backend + SymPy math engine
│   │   ├── app/
│   │   ├── tests/            # pytest (65 tests, 100% coverage)
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── web/                  # Next.js 15 + React 19 + TypeScript
│       ├── app/              # App Router pages (landing, dashboard, exam)
│       ├── components/       # Button, Card, Badge, Navbar, StatCard, CountdownTimer
│       ├── lib/              # Utility helpers
│       ├── styles/           # Global CSS (design tokens)
│       ├── __tests__/        # jest (63 tests, 100% coverage)
│       └── Dockerfile
├── packages/
│   └── design-tokens/        # Shared design tokens (JSON + CSS)
├── schools/
│   └── cau_giay/             # Multi-tenant per-school data
├── schemas/                  # JSON schemas (future)
├── docs/
│   └── plans/                # Master plans and architecture docs
├── infra/
│   ├── ci/
│   └── docker/
├── .github/workflows/
│   └── ci.yml                # Backend + frontend + duplication CI
├── .jscpd.json               # jscpd config (threshold <2.5%)
├── docker-compose.yml        # Postgres + Redis + Backend + Web
└── README.md
```

## Quality Gates

- **Backend coverage**: ≥85% (pytest-cov)
- **Frontend coverage**: ≥85% (jest)
- **Code duplication**: <2.5% (jscpd)
- **Lint**: ruff (Python), ESLint (TS)

Current state: backend 100%, frontend 100%, duplication 0%.

## Quick Start

### With Docker (recommended)

```bash
cd SourceCode/DailyExam
docker compose up --build
# Web:     http://localhost:3000
# Backend: http://localhost:8000
# Docs:    http://localhost:8000/docs
```

### Local dev — Backend

```bash
cd apps/backend
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                        # Run tests with coverage
.venv/bin/uvicorn app.main:app --reload # Start dev server on 8000
```

### Local dev — Frontend

```bash
cd apps/web
npm install
npm test                                # Run tests with coverage
npm run dev                             # Start dev server on 3000
```

### Duplication check

```bash
npx jscpd .
```

## Architecture

- **Code**: generic engine, deployed once
- **Data**: per-school configs + templates (multi-tenant)
- **Rule**: No `if school == 'xyz'` in engine — all behavior from `school_config`

See `docs/plans/master_plan_v4.md` for the full 14-week roadmap.
See `docs/plans/multi_tenant_framework_v1.md` for the school onboarding framework.

## License

Private.

## Credits

Co-Authored-By: Craft Agent <agents-noreply@craft.do>
