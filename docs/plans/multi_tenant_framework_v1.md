# Multi-Tenant School Onboarding Framework v1

**Date**: 2026-11-05  
**Project**: Math Exam Platform  
**Pilot school**: Cầu Giấy

## Core Principle

> **Everything school-specific = DATA, not CODE**

Engine code deployed once. Adding a new school = adding data files only. Zero code changes required.

## 6-Step Onboarding Pipeline

| Step | Action | Who | Time | Output |
|---|---|---|---|---|
| 1 | Collect raw exams | Admin | 15 min | `schools/{slug}/raw/` |
| 2 | Analyze & extract | AI | 30-60 min | `analysis/` folder |
| 3 | Generate config | AI | 10 min | `school_config.json` |
| 4 | Generate templates | AI | 1-2 hr | 25-30 school templates |
| 5 | Verify & review | GV | 30 min | Approval + corrections |
| 6 | Register & deploy | Automated | 5 min | School live in production |

**Total**: ~1-2 days per school, zero engineer time.

## System Architecture

### Code (1 codebase, generic)
- `engine/` — template resolver, exam composer, grader, scheduler
- `onboarding/` — CLI framework (6 steps automated)
- `schemas/` — JSON schemas validate everything
- `apps/` — multi-tenant web/admin

### Data (per school)
- `core_templates/` — 100 shared templates
- `schools/{slug}/` — per-school data folder
  - `raw/` — original exams
  - `analysis/` — AI analysis reports
  - `config/school_config.json` — behavior config
  - `templates/` — 25-30 school-specific templates

### Database
- `schools` — school metadata
- `school_configs` — JSONB configs
- `core_templates` — shared
- `school_templates` — per-school
- `daily_exam` — generated exams
- `student_submission` — HS answers + grades

## Key Design Rule

Engine code must NEVER have `if school == 'xyz'`. All behavior driven by `school_config`.

```python
def generate_daily_exam(school_id, date):
    config = db.get_school_config(school_id)
    templates = resolver.resolve_templates(config)
    exam = composer.compose(templates, config)
    exam = stylist.apply_style(exam, config)
    db.save(school_id, date, exam)
```

## Pilot Plan: Cầu Giấy First

Target: onboard Cầu Giấy with 7 existing exam files (2019-2026) as the first school.

### Data available
- 7 past exams (CauGiay-2019-2020.docx through CauGiay-2025-2026.docx)
- ~46-57 KB each

### Expected outputs after onboarding
- `cau_giay_style_config.json`
- ~100 questions extracted into bank
- 30 school-specific templates
- 3 sample exams for GV approval

## Scaling Projection

| Phase | Schools | Time to add new school | Code changes |
|---|---|---|---|
| Pilot | 1 (Cầu Giấy) | - | - |
| Early | 5 | 1-2 days each | 0 |
| Scale | 50 | 1 day each (streamlined) | 0 |
| Mature | 500+ | Self-service (GV wizard) | 0 |

## Framework Evolution Roadmap

- **v1**: CLI-based, technical admin
- **v2**: Web UI wizard, GV self-service
- **v3**: Clone-from-template, marketplace, auto-tuning

## Next Steps

1. Finalize full master plan incorporating this framework
2. Build core engine (Phase 1-2 of master plan)
3. Build onboarding CLI (Phase 2.5)
4. Pilot with Cầu Giấy as first school
5. Validate framework → onboard 2nd school (Amsterdam or Trần Đại Nghĩa)

## Open Questions

- Pricing per school tier (A/B/C)?
- Template sharing between schools?
- Versioning strategy for templates/configs?
- GV override permissions on auto-gen exams?
