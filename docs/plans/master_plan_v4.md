# Master Plan v4 — Math Exam Platform

**Date**: 2026-11-05
**Pilot school**: THCS Cầu Giấy
**Target launch**: Tuần 2 tháng 2/2027 (14 tuần từ start)

## 1. Vision

Xây dựng nền tảng tự động sinh đề + chấm bài môn Toán tiểu học/THCS, pilot với Cầu Giấy, kiến trúc multi-tenant để dễ onboard trường mới mà không sửa code.

## 2. Core Concepts (đã chốt)

- **Daily exam model**: 1 trường / 1 ngày / 1 đề dùng chung
- **Schedule**: Gen 5h sáng → mở cổng 8h → đóng 9h → release kết quả 9h30
- **Grading**: Reference-based (so với lời giải chuẩn sinh cùng đề)
- **Multi-tenant**: Data-driven, mọi behavior của trường qua config
- **LLM provider**: Claude Haiku 4.5 primary, Sonnet 4.6 escalation
- **Accuracy target**: >90% cho tự luận, >99% cho TN/điền số
- **Anti-cheat**: Shuffle câu + đáp án per HS, timer cố định

## 3. Architecture

### Three-layer template system
- Layer 1: 100 core templates (shared across schools)
- Layer 2: 30 school-specific templates per school
- Layer 3: `school_config.json` (per school style)

### Code vs Data separation
- Engine code: generic, 1 codebase
- All school behavior: driven by `school_config.json`
- Rule: NO `if school == 'xyz'` in engine code

### Tech stack
- Backend: Python 3.12 + FastAPI
- Math engine: SymPy
- LLM: anthropic SDK + openai (fallback)
- DB: PostgreSQL + Redis
- Queue: Celery + Redis
- Frontend: Next.js 15 + TypeScript + shadcn/ui + KaTeX
- Deploy: Docker + Railway/Fly.io (MVP), K8s (scale)

## 4. Roadmap — 14 tuần, 6 phases

### Phase 1 — Foundation (Tuần 1-2)
Mục tiêu: Nền tảng code + schema, không business logic.

- Chốt 37 chuyên đề + TV display names
- Thiết kế 6 JSON schemas: template, exam, grading_result, school_config, submission, chuyen_de
- Setup repo + CI/CD + Docker compose dev
- PostgreSQL migrations + Redis setup
- LLM client wrapper + prompt caching helper
- SymPy math engine wrapper

Deliverable: `make up` → dev environment chạy, tất cả schema validated.

### Phase 2 — Core Template Bank (Tuần 3-4)
Mục tiêu: 100 templates dùng chung + engine chạy templates.

- Template engine core (load, validate, sample params)
- Param sampler + constraint solver
- SymPy solver wrapper + verifier
- Context pool manager (bối cảnh, nhân vật, đơn vị)
- Viết 100 core templates:
  - Số học cơ bản: 25
  - Bài toán có lời văn: 25
  - Hình học: 20
  - Phân số/tỉ lệ: 15
  - Dãy số/quy luật: 10
  - Logic/suy luận: 5
- Unit tests + auto-verify suite

Deliverable: CLI `python gen_sample.py --template=X --count=5` chạy được.

### Phase 3 — Multi-tenant Onboarding Framework (Tuần 5-6)
Mục tiêu: Pipeline onboard trường mới + onboard Cầu Giấy.

- 6-step onboarding CLI: `onboard.py {init|analyze|gen-config|gen-templates|verify|deploy}`
- Step 2: LLM analyzer (phân tích đề cũ → style patterns)
- Step 3: Config generator (sinh school_config.json)
- Step 4: Template generator (sinh 30 school templates)
- Step 5: Auto-verify + sample exam generator
- Step 6: Deploy script (DB insert + cron register)
- **Chạy pipeline cho Cầu Giấy**: 7 đề 2019-2026 → config + 30 templates

Deliverable: Cầu Giấy có đầy đủ data trong DB, template resolver load được.

### Phase 4 — Daily Exam Generator (Tuần 7-8)
Mục tiêu: Cron 5h sáng tự gen đề cho mọi trường active.

- Exam composer (chọn 10 bài theo weights + difficulty dist)
- Difficulty balancer (NB/TH/VD/VDC distribution)
- LLM paraphrase service (với style injection)
- LLM narrator (viết lời giải văn)
- Verify loop (gen → verify → retry → fallback)
- Backup exam system (gen 7 đề/tuần vào Chủ Nhật 23h)
- Cron scheduler (5h daily per school)
- Alert system (báo GV khi gen lỗi)
- GV review window 6h-8h

Deliverable: Mỗi 5h sáng, DB có 1 daily_exam cho Cầu Giấy ready.

### Phase 5 — Grader Service (Tuần 9-10)
Mục tiêu: Chấm bài >90% accuracy.

- MCQ grader (exact match)
- Numeric grader (SymPy comparison, tolerance)
- Essay parser (LLM extract structured steps)
- Reference-based essay grader (so với lời giải chuẩn)
- Prompt caching (rubric + đề + lời giải cache mạnh)
- Self-consistency (3 runs + majority vote)
- Confidence scoring + escalation logic
- Feedback generator (lời khuyên cho HS)
- Teacher review queue (bài confidence <0.85)
- Benchmark trên 500 bài golden → tune prompts

Deliverable: API `/grade` + `/grade/batch`, accuracy report >90%.

### Phase 6 — UI + Pilot + Launch (Tuần 11-14)

#### Student portal
- Login (email + OTP)
- Daily exam view (8h-9h window)
- Exam taking UI (MCQ + numeric input + essay editor với KaTeX)
- Result view (sau 9h30) với feedback chi tiết
- Dashboard: chuyên đề mạnh/yếu, lịch sử
- Practice mode (làm đề cũ)

#### Teacher portal
- Dashboard: xem đề hôm nay, status
- Review queue (bài confidence thấp)
- Class analytics (chuyên đề lớp yếu)
- Student profile (xem HS cụ thể)
- Override exam (nếu muốn thay đề)

#### Admin portal
- School config editor
- Template management
- Schedule config (đổi giờ gate open/close)
- System health monitoring

#### Pilot + Launch
- Load test 1000 concurrent
- Pilot 1 lớp Cầu Giấy (2 tuần)
- Fix bugs + tune
- Pilot mở rộng 3-5 lớp
- Soft launch

Deliverable: System live, 100+ HS Cầu Giấy đang dùng thực tế.

## 5. Budget

### One-time costs
- LLM API cho development: $200
- LLM API cho onboard Cầu Giấy (analyze + gen templates): $20
- LLM API cho gen initial exam bank (30 ngày x $0.07): $2
- Infra setup: $100
- Domain + SSL: $50
- **Total**: ~$400

### Operational (monthly, 1 trường 500 HS)
- Gen đề daily: $2
- Chấm bài: $96
- Infra (DB, Redis, workers, web): $100
- **Total**: ~$200/tháng = $0.40/HS/tháng

### Dev effort
- 1 full-stack lead: 14 tuần
- 1 ML engineer (part-time): Phase 2-5 (8 tuần)
- 1 frontend dev: Phase 6 (4 tuần)
- 0.3 GV cố vấn: toàn bộ 14 tuần
- QA: Phase 5-6 (6 tuần, 0.5 FTE)

## 6. Key Milestones

| Tuần | Milestone |
|---|---|
| 2 | Dev environment ready |
| 4 | 100 core templates working |
| 6 | Cầu Giấy fully onboarded (data level) |
| 8 | Daily exam auto-gen chạy đúng 5h sáng |
| 10 | Grader đạt >90% trên golden set |
| 12 | Full UI ready |
| 13 | Pilot with 1 class |
| 14 | Soft launch |

## 7. Risk Register

| Rủi ro | Xác suất | Impact | Mitigation |
|---|---|---|---|
| Accuracy <90% tự luận | Trung bình | Cao | Reference-based + self-consistency + human escalation |
| 1 đề gen sai → ảnh hưởng toàn trường | Trung bình | Rất cao | Multi-step verify + backup exam + GV review window |
| LLM API rate limit | Thấp | Trung bình | Multi-provider fallback + queue |
| HS gian lận trong khung giờ | Trung bình | Trung bình | Shuffle câu + đáp án + timer hẹp |
| GV không chịu dùng | Trung bình | Cao | Onboarding kỹ + training + feedback loop |
| Scale vượt dự kiến | Thấp | Trung bình | Horizontal scaling + batch API |

## 8. Success Metrics (Post-launch)

| Metric | Target |
|---|---|
| Daily active students | >80% enrolled |
| Grading accuracy | >90% |
| Exam gen success rate | >99% (<1% fallback to backup) |
| Student satisfaction | >4/5 |
| Teacher satisfaction | >4/5 |
| Avg grading latency | <3s |
| Uptime | >99.5% |
| Cost per student/month | <$0.50 |

## 9. Post-MVP Roadmap

### V2 (tháng 4-6)
- Onboard trường thứ 2 (Amsterdam hoặc TĐN)
- Mobile app (React Native)
- Adaptive practice (gợi ý bài theo level HS)
- Parent portal

### V3 (tháng 7-12)
- Multi-grade per school (lớp 4, 5, 6 riêng)
- OCR bài viết tay
- Marketplace templates
- B2C mode (HS tự đăng ký luyện thi)

## 10. Open Decisions

Những điểm cần chốt trước khi start Phase 1:

1. Scope cấp học: Chỉ lớp 5 (thi tuyển sinh 6)? Hay cả lớp 4-5 + 6-9?
2. Số câu/đề: 10 câu fix? Hay config theo trường?
3. Model kinh doanh: B2B (trường) hay B2C (HS/PH) hay cả hai?
4. Hosting: Railway/Fly.io (nhanh) hay VPS VN (compliance)?
5. Team size: Solo? 2-3? 5+?
6. Mobile: Web-only v1, mobile v2? Hay PWA v1?
7. LLM privacy: Chấp nhận Anthropic/OpenAI xử lý US? Hay cần on-premise?
8. Pricing B2B: Per student? Per school? Flat fee?
9. Có cần export đề PDF cho thi giấy không?
10. GV được quyền tạo template thủ công không?
