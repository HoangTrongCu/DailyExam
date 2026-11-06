'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { StatCard } from '@/components/StatCard';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { useAuth } from '@/components/AuthProvider';
import { api, type AnalyticsEntry, type Submission } from '@/lib/api';

const CD_LABELS: Record<string, string> = {
  trung_binh_cong: 'Trung bình cộng',
  ti_so_phan_tram: 'Tỉ số phần trăm',
  hinh_hoc: 'Hình học',
  bai_toan_tuoi: 'Bài toán tuổi',
  chuyen_dong: 'Chuyển động',
  phan_so: 'Phân số',
  ti_le: 'Tỉ lệ',
  day_so: 'Dãy số',
  dirichlet: 'Dirichlet',
  cong_viec_chung: 'Công việc chung',
};

function chuyenDeLabel(key: string): string {
  return CD_LABELS[key] ?? key;
}

interface TopicListProps {
  title: string;
  description: string;
  loading: boolean;
  emptyText: string;
  topics: AnalyticsEntry[];
  bg: string;
  badgeVariant: 'success' | 'warning';
}

function TopicListCard({ title, description, loading, emptyText, topics, bg, badgeVariant }: TopicListProps) {
  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
      {loading && <p style={{ marginTop: 16 }}>Đang tải...</p>}
      {!loading && topics.length === 0 && (
        <p style={{ marginTop: 16, color: 'var(--color-muted-fg)' }}>{emptyText}</p>
      )}
      <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {topics.map((t) => (
          <li
            key={t.chuyen_de}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: 12,
              background: bg,
              borderRadius: 'var(--radius-md)',
            }}
          >
            <span style={{ fontWeight: 600 }}>{chuyenDeLabel(t.chuyen_de)}</span>
            <Badge variant={badgeVariant}>{t.average_score_10}/10</Badge>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [submissions, setSubmissions] = React.useState<Submission[]>([]);
  const [analytics, setAnalytics] = React.useState<AnalyticsEntry[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!user) {
      const t = setTimeout(() => router.push('/login'), 200);
      return () => clearTimeout(t);
    }
    Promise.all([api.mySubmissions(user.access_token), api.myAnalytics(user.access_token)])
      .then(([s, a]) => {
        setSubmissions(s);
        setAnalytics(a);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, [user, router]);

  if (!user) return null;

  const avg =
    submissions.length > 0
      ? submissions.reduce((acc, s) => acc + s.percentage, 0) / submissions.length
      : 0;
  const strong = analytics.filter((a) => a.average_score_10 >= 7).slice(0, 5);
  const weak = analytics.filter((a) => a.average_score_10 < 6).slice(0, 5);
  const today = new Date().toISOString().slice(0, 10);

  return (
    <>
      <Navbar userName={user.full_name} schoolName="THCS Cầu Giấy" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div style={{ marginBottom: 32 }}>
          <Badge variant="info">{new Date().toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' })}</Badge>
          <h1 style={{ fontSize: 40, marginTop: 12 }}>Chào {user.full_name}! 🚀</h1>
          <p style={{ color: 'var(--color-muted-fg)', marginTop: 8, fontSize: 18 }}>
            Đề thi hôm nay đã sẵn sàng. Mở cổng từ 8:00 sáng.
          </p>
        </div>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--spacing-6)',
            marginBottom: 'var(--spacing-10)',
          }}
          aria-label="Thống kê tổng quan"
        >
          <StatCard label="Đề đã làm" value={submissions.length} icon="📘" tone="primary" />
          <StatCard label="Điểm TB" value={avg.toFixed(1) + '%'} icon="⭐" tone="secondary" />
          <StatCard label="Chuyên đề luyện" value={analytics.length} icon="📚" tone="accent" />
          <StatCard label="Hạng" value="#5" icon="🏆" tone="success" trend="+2 bậc" />
        </section>

        <Card tone="primary" elevated style={{ marginBottom: 'var(--spacing-10)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 20 }}>
            <div>
              <CardTitle>📝 Đề thi hôm nay</CardTitle>
              <CardDescription>
                10 câu · 60 phút · Bao gồm trung bình cộng, hình học, phân số...
              </CardDescription>
              <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Badge variant="info">Mở 8:00</Badge>
                <Badge variant="warning">Đóng 9:00</Badge>
                <Badge variant="success">Kết quả 9:30</Badge>
              </div>
            </div>
            <Link href="/exam">
              <Button variant="primary" size="lg">
                Vào làm bài →
              </Button>
            </Link>
          </div>
        </Card>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 'var(--spacing-6)',
          }}
        >
          <TopicListCard
            title="⭐ Chuyên đề bạn giỏi"
            description="Dựa trên các bài đã nộp"
            loading={loading}
            emptyText="Hãy làm bài đầu tiên để xem thống kê!"
            topics={strong}
            bg="var(--color-blue-50)"
            badgeVariant="success"
          />
          <TopicListCard
            title="⚠️ Chuyên đề cần luyện"
            description="Dành 10 phút mỗi ngày để giỏi hơn!"
            loading={loading}
            emptyText="Bạn đang rất tốt! Chưa có chuyên đề nào yếu."
            topics={weak}
            bg="#FEF3C7"
            badgeVariant="warning"
          />
        </section>

        {submissions.length > 0 && (
          <section style={{ marginTop: 'var(--spacing-10)' }}>
            <Card>
              <CardTitle>📜 Lịch sử gần đây</CardTitle>
              <ul style={{ listStyle: 'none', marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {submissions.slice(0, 5).map((s) => (
                  <li
                    key={s.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: 12,
                      background: 'var(--color-slate-50)',
                      borderRadius: 'var(--radius-md)',
                    }}
                  >
                    <div>
                      <strong>Đề {s.exam_id.split(':')[1]}</strong>
                      <div style={{ fontSize: 13, color: 'var(--color-muted-fg)' }}>
                        {new Date(s.graded_at).toLocaleString('vi-VN')}
                      </div>
                    </div>
                    <Badge variant={s.percentage >= 80 ? 'success' : s.percentage >= 50 ? 'warning' : 'danger'}>
                      {s.total_score.toFixed(1)}/{s.max_total_score.toFixed(1)}
                    </Badge>
                  </li>
                ))}
              </ul>
            </Card>
          </section>
        )}
      </main>
    </>
  );
}
