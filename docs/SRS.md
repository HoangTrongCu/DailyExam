# Software Requirements Specification (SRS)

**Product**: DailyExam — Nền tảng luyện thi tuyển sinh lớp 6 trường chất lượng cao
**Version**: 1.0 (MVP)
**Date**: 2026-11-07
**Author**: BA (via requirements elicitation với client)
**Status**: Ready for development

---

## 1. Introduction

### 1.1 Purpose
Tài liệu này mô tả đầy đủ **yêu cầu chức năng và phi chức năng** cho MVP của nền tảng DailyExam, dùng làm nguồn chính thức (source of truth) cho đội phát triển.

### 1.2 Scope (MVP)
- **Môn**: Toán
- **Lớp**: 5 (tuyển sinh lớp 6)
- **Kỳ thi mục tiêu**: Trường THCS chất lượng cao Hà Nội (pilot: Cầu Giấy)
- **Người dùng**: Phụ huynh (payer) + Học sinh (end user)
- **Phạm vi địa lý**: Hà Nội
- **Không có trong MVP**: Payment, feature gating, group pricing, GV portal, mobile native app

### 1.3 Definitions
- **Đề**: Bài kiểm tra 1 trường / 1 ngày, gồm nhiều câu hỏi
- **Blueprint**: Cấu hình cấu trúc đề của 1 trường (số câu, loại câu, phân bổ chuyên đề, mức độ)
- **Phúc khảo**: HS báo bài chấm sai → admin review → nếu đúng thì sửa lời giải và auto-regrade
- **Chuyên đề**: Lĩnh vực toán (TBC, phần trăm, hình học...)
- **NB/TH/VD/VDC**: Nhận biết / Thông hiểu / Vận dụng / Vận dụng cao (chuẩn VN)

---

## 2. Overall Description

### 2.1 Vision
> Nền tảng luyện thi tuyển sinh cấp 2 duy nhất mang lại **chất lượng đề như đề thật của từng trường**, chấm tự động cả trắc nghiệm và tự luận, giúp HS luyện mỗi ngày và PH thấy rõ sự tiến bộ.

### 2.2 Problem Statement
HS luyện thi hiện nay gặp 6 pain points:
1. Đề cố định, lặp lại
2. Chỉ chấm được trắc nghiệm
3. Nhiều app = nhiều account
4. Không theo dõi được tiến bộ
5. Thi chuyển cấp 2 không có hệ thống luyện online
6. PH mù thông tin về năng lực con

### 2.3 Personas
- **Minh (HS lớp 5, 10 tuổi)**: dùng iPad/laptop, thiếu tự giác, động lực = được khen + PH ép
- **Chị Hương (PH, 38)**: bận, không muốn app riêng, muốn email weekly, budget 100-200k/tháng
- **Admin (anh — solo founder)**: hằng ngày check, cần dashboard + queue phúc khảo

### 2.4 Constraints
- Budget < 100 triệu VND
- Team: solo
- Timeline MVP: 4 tuần
- Hosting: AWS
- LLM: Claude Haiku 4.5

---

## 3. Business Rules

### 3.1 Exam Lifecycle
```
Mỗi ngày 5h sáng  → Auto-gen 1 đề mới + lời giải / trường
                   → Status = 'open'
Cùng ngày 0h đêm  → Status = 'makeup' (HS làm được nhưng KHÔNG tính ranking)
0h Chủ nhật       → Status = 'closed' (vĩnh viễn, không truy cập)
                   → KHÔNG xoá — giữ trong DB để reuse
```

### 3.2 Ranking (3 cấp, per trường)
- **Rank đề**: trong 1 đề, thứ hạng số thứ tự (`#12 / 420`)
- **Rank tuần**: tổng điểm 7 đề tuần đó
- **Rank tổng**: tổng điểm từ đầu đến giờ

HS luyện nhiều trường = có nhiều bộ ranking riêng (không gộp). Đề làm bù không tính ranking.

### 3.3 Appeal Loop (USP)
```
HS xem kết quả → "Báo bài chấm sai" + lý do
  ↓
Queue admin phúc khảo
  ↓
Admin xem
  ├─ HS đúng → Sửa lời giải chuẩn
  │            → Hệ thống AUTO REGRADE tất cả submissions trên đề này
  │            → Email thông báo HS/PH bị ảnh hưởng
  └─ LLM đúng → Trả lời giải thích, không đổi điểm
```

### 3.4 Access Model
- HS truy cập đề của **mọi trường** trong hệ thống (không đăng ký trường)
- MVP: **tất cả miễn phí** không giới hạn
- V2: free trial 7 ngày × 7 đề; paid không giới hạn

### 3.5 Account Flow
- PH đăng ký cho con (email PH)
- **Email verify bắt buộc** → active
- 1 HS = 1 account, 1 session active (kick cũ)
- Xoá: soft 30 ngày → hard delete

### 3.6 Session Integrity (khi làm đề)
- Timer 60 phút (tính theo blueprint trường)
- Auto-save từng câu HS nộp
- Reload / chuyển thiết bị → resume, timer không reset
- Mất mạng → reconnect 10 lần → fail hết thì auto-submit

---

## 4. Functional Requirements (MoSCoW)

### 4.1 MUST (22 features — required cho launch)

#### Auth & Users
| ID | Feature |
|---|---|
| FR-M1 | PH đăng ký tài khoản con với email + password + tên HS |
| FR-M2 | Email verification bắt buộc (link trong email) |
| FR-M3 | Login email + password → nhận JWT |
| FR-M4 | Reset password qua email (link hiệu lực 15 phút) |
| FR-M5 | 1 active session / account — login mới kick thiết bị cũ |

#### Learner (HS)
| ID | Feature |
|---|---|
| FR-M6 | Dashboard HS: xem đề hôm nay của **tất cả** trường |
| FR-M7 | Click vào đề → confirmation modal → bắt đầu làm |
| FR-M8 | Timer 60 phút đếm ngược, auto-save từng câu khi HS trả lời |
| FR-M9 | Resume từ thiết bị khác / sau reload — timer giữ nguyên |
| FR-M10 | Reconnect tự động nếu mất mạng; 10 lần fail → auto-submit |
| FR-M11 | Nộp bài → NGAY hiển thị điểm + lời giải chi tiết |
| FR-M12 | Xem lịch sử bài đã làm |
| FR-M13 | Làm bù đề cũ trong tuần (status='makeup', KHÔNG tính ranking) |
| FR-M14 | Nút "Báo bài chấm sai" trên từng câu kết quả, kèm form lý do |

#### Ranking & Analytics
| ID | Feature |
|---|---|
| FR-M15 | Ranking per trường, 3 cấp (đề/tuần/tổng), hiển thị thứ hạng số |
| FR-M16 | Analytics chuyên đề mạnh/yếu (biểu đồ + top 3 yếu) |

#### Exam Generation & Grading
| ID | Feature |
|---|---|
| FR-M17 | Cron 5h sáng: auto-gen 1 đề/trường/ngày; gen đề + lời giải cùng lúc |
| FR-M18 | Đóng đề status='makeup' lúc 0h; đóng 'closed' lúc 0h CN |
| FR-M19 | Chấm TN exact match + điền số SymPy tolerance |
| FR-M20 | Chấm tự luận bằng Claude Haiku 4.5 (reference-based) |

#### Admin
| ID | Feature |
|---|---|
| FR-M21 | Admin dashboard: users, bài nộp, queue phúc khảo, system health |
| FR-M22 | Admin phúc khảo: sửa lời giải → auto regrade all + email users bị ảnh hưởng |

#### Email
| ID | Feature |
|---|---|
| FR-M23 | Email cho PH sau mỗi lần HS nộp bài (điểm + link xem chi tiết) |

#### Blueprint
| ID | Feature |
|---|---|
| FR-M24 | Admin upload blueprint JSON cho trường (không UI editor trong MVP) |

### 4.2 SHOULD (có thì tốt)

| ID | Feature |
|---|---|
| FR-S1 | Email weekly report cho PH (đầy đủ stats) |
| FR-S2 | Email alert khi HS bỏ 2 ngày liên tiếp |
| FR-S3 | Digital badge + confetti sau khi nộp bài |
| FR-S4 | Streak counter (ngày liên tiếp làm đề) |
| FR-S5 | Top rankers hiện trên landing/dashboard |
| FR-S6 | Anti-download basic (disable right-click/copy/print CSS) |
| FR-S7 | Admin ban/unban user spam |
| FR-S8 | Admin fix điểm manual (ngoài appeal loop) |
| FR-S9 | Export CSV users / submissions |
| FR-S10 | Delete account (soft 30d → hard delete) |

### 4.3 COULD

| ID | Feature |
|---|---|
| FR-C1 | Percentile comparison |
| FR-C2 | Reward quà thật manual flow |
| FR-C3 | 404/500 pages thân thiện |
| FR-C4 | PWA shell |
| FR-C5 | Dark mode |

### 4.4 WON'T (V2+)

- Payment gateway (QR, VNPay, Momo, ZaloPay)
- Trial / Paid feature gating
- License expiration logic
- Group pricing (≥5 account −15%)
- PH portal riêng
- Blueprint Studio UI
- Smart exam recommendation
- Shuffle câu / đáp án

---

## 5. Non-Functional Requirements

### 5.1 Performance
| Metric | Target |
|---|---|
| Concurrent users MVP | 100 |
| Dashboard load | <2s |
| Submit TN/numeric | <2s |
| Submit essay | <5s (acceptable 5-10s peak) |

### 5.2 Security (Level A — MVP)
- Password bcrypt / PBKDF2 ≥100k iterations
- HTTPS everywhere, JWT 7-day
- Email verify bắt buộc
- 1 active session / account
- No captcha / rate limit (MVP)

### 5.3 Privacy (Nghị định 13/2023)
- Data minimization
- Parental consent checkbox khi đăng ký
- Privacy Policy + T&C accessible
- Delete account: soft 30 ngày → hard delete cascade

### 5.4 Devices & Browsers
- Responsive: desktop + tablet + mobile (3 equal priority)
- Browsers: Chrome/Safari/Firefox/Edge versions gần đây

### 5.5 Design System
- Style: **Claymorphism (Gamified Edu)**
- Palette: Primary amber `#D97706` + secondary yellow `#F59E0B` + accent green `#059669` + background cream `#FFFBEB`
- Fonts: Baloo 2 (heading) + Comic Neue (body)
- Illustrations: chibi/cute, Lottie animations
- Border radius: 20-40px, colorful soft shadows

### 5.6 Infrastructure
- Hosting: AWS (ECS Fargate + RDS Postgres + S3 + CloudFront)
- LLM: Claude Haiku 4.5 (prompt caching enabled)
- Email: Resend/SES
- Backup: RDS auto-snapshot daily, 7-day retention

### 5.7 Operating Cost Estimate
- MVP (100 users): ~$40-60/tháng
- 500 users: ~$150-250/tháng

---

## 6. External Interfaces

### 6.1 User Interfaces (summary)
| Page | URL | Who |
|---|---|---|
| Landing | `/` | Public |
| Register | `/register` | Public |
| Email verify | `/verify/:token` | Public |
| Login | `/login` | Public |
| Forgot password | `/forgot-password`, `/reset/:token` | Public |
| Dashboard | `/dashboard` | HS |
| Take exam | `/exam/:id` | HS |
| Result | `/exam/:id/result` | HS |
| History | `/history` | HS |
| Analytics | `/analytics` | HS |
| Admin dashboard | `/admin` | Admin |
| Admin appeals | `/admin/appeals` | Admin |
| Admin blueprints | `/admin/blueprints` | Admin |

### 6.2 External APIs
- Claude Haiku 4.5 API (essay grading)
- Resend API (transactional email)

---

## 7. Data Model (overview — see SDD for full ERD)

Core entities:
- `schools` — 7 trường CLC Hà Nội
- `blueprints` — cấu hình gen đề của từng trường
- `templates` — template toán core (reusable)
- `exams` — đề của mỗi ngày, mỗi trường
- `questions` — câu hỏi trong đề (snapshot)
- `users` — PH + HS, admin
- `submissions` — bài làm HS (có answers + results)
- `appeals` — phúc khảo (HS → admin)
- `analytics` — rollup per student+chuyen_de
- `email_log` — email đã gửi

---

## 8. Acceptance Criteria (MVP launch gate)

MVP được coi là **sẵn sàng launch** khi:

- [ ] Backend coverage ≥85%, Frontend coverage ≥85%, Duplication <2.5%
- [ ] Toàn bộ 22 FR-Must + tối thiểu 5 FR-Should hoạt động
- [ ] 1 blueprint Cầu Giấy upload, gen được đề đúng cấu trúc
- [ ] 1 HS đăng ký → verify email → làm 3 đề → có ranking + analytics
- [ ] 1 PH nhận email sau khi HS nộp bài
- [ ] 1 admin phúc khảo → sửa lời giải → tất cả submissions được regrade
- [ ] Responsive: test trên Chrome desktop + Safari iPad + Chrome mobile
- [ ] Load test 100 concurrent OK
- [ ] Privacy Policy + T&C published
- [ ] Deploy live trên AWS (hoặc staging → prod flow qua CI)

---

## 9. Open Questions (sau MVP)

- Giá license cụ thể (chốt sau khi có cost thực)
- Chi tiết payment gateway (V2)
- Brand name có đổi không? (hiện giữ DailyExam)
- Timing email weekly report (thứ mấy, giờ nào)
