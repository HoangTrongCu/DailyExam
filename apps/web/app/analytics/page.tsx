'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { useAuth } from '@/components/AuthProvider';
import { api, type AnalyticsEntry } from '@/lib/api';

const CD_LABELS: Record<string, string> = {
  trung_binh_cong: 'Trung bình cộng',
  ti_so_phan_tram: 'Tỉ số phần trăm',
  hinh_hoc: 'Hình học',
  bai_toan_tuoi: 'Bài toán tuổi',
  chuyen_dong: 'Chuyển động',
  phan_so: 'Phân số',
  ti_le: 'Tỉ lệ',
};

function labelOf(k: string) { return CD_LABELS[k] ?? k; }

export default function AnalyticsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [data, setData] = React.useState<AnalyticsEntry[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    api.myAnalytics(user.access_token).then(setData).catch(() => undefined).finally(() => setLoading(false));
  }, [user, router]);

  if (!user) return null;

  const strong = data.filter(d => d.average_score_10 >= 7).slice(0, 5);
  const weak = data.filter(d => d.average_score_10 < 6).slice(0, 5);

  return (
    <>
      <Navbar label="Thống kê tiến bộ" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 36, marginBottom: 24 }}>📊 Phân tích chuyên đề</h1>

        {loading && <Card>Đang tải...</Card>}
        {!loading && data.length === 0 && (
          <Card>
            <CardTitle>Chưa có dữ liệu</CardTitle>
            <CardDescription>Làm ít nhất 1 bài để xem thống kê.</CardDescription>
          </Card>
        )}

        {!loading && data.length > 0 && (
          <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
            <TopicList title="⭐ Chuyên đề bạn giỏi" description="Điểm TB ≥ 7/10"
                       items={strong} badge="success" emptyText="Hãy luyện thêm để đạt mức này!" />
            <TopicList title="⚠️ Cần luyện thêm" description="Điểm TB < 6/10"
                       items={weak} badge="warning" emptyText="Bạn đang rất tốt! 🎉" />
          </section>
        )}
      </main>
    </>
  );
}

interface TopicListProps {
  title: string; description: string; items: AnalyticsEntry[];
  badge: 'success' | 'warning'; emptyText: string;
}

function TopicList({ title, description, items, badge, emptyText }: TopicListProps) {
  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
      {items.length === 0 ? (
        <p style={{ marginTop: 16, color: 'var(--color-muted-fg)' }}>{emptyText}</p>
      ) : (
        <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {items.map((t) => (
            <li key={`${t.school_id}:${t.chuyen_de}`} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: 12,
              background: badge === 'success' ? 'var(--green-50)' : 'var(--amber-50)',
              borderRadius: 'var(--radius-md)',
            }}>
              <span style={{ fontWeight: 600 }}>{labelOf(t.chuyen_de)}</span>
              <Badge variant={badge}>{t.average_score_10}/10</Badge>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
