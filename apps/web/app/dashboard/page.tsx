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
import { api, type ExamSummary, type Submission } from '@/lib/api';

const STATUS_LABEL: Record<string, string> = {
  open: '🟢 Đang mở',
  makeup: '🟡 Làm bù',
  closed: '🔴 Đã đóng',
};

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [exams, setExams] = React.useState<ExamSummary[]>([]);
  const [subs, setSubs] = React.useState<Submission[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!user) {
      const t = setTimeout(() => router.push('/login'), 200);
      return () => clearTimeout(t);
    }
    Promise.all([
      api.examsToday(user.access_token).catch(() => []),
      api.mySubmissions(user.access_token).catch(() => []),
    ]).then(([e, s]) => { setExams(e); setSubs(s); }).finally(() => setLoading(false));
  }, [user, router]);

  if (!user) return null;

  const avg = subs.length > 0 ? subs.reduce((a, s) => a + s.percentage, 0) / subs.length : 0;

  return (
    <>
      <Navbar label="HS · Luyện thi vào lớp 6 CLC" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: 32 }}>
          <Badge variant="info">{new Date().toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit' })}</Badge>
          <h1 style={{ fontSize: 40, marginTop: 12 }}>Chào {user.full_name}! 🚀</h1>
          <p style={{ color: 'var(--color-muted-fg)', fontSize: 18, marginTop: 8 }}>
            Hôm nay có {exams.length} đề mới đang chờ bạn.
          </p>
        </div>

        <section style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 24, marginBottom: 40,
        }}>
          <StatCard label="Đề đã làm" value={subs.length} icon="📘" tone="primary" />
          <StatCard label="Điểm TB" value={`${avg.toFixed(1)}%`} icon="⭐" tone="secondary" />
          <StatCard label="Streak 🔥" value={calculateStreak(subs)} icon="🔥" tone="warm" />
          <StatCard label="Huy hiệu" value={Math.min(subs.length * 2, 24)} icon="🏅" tone="accent" />
        </section>

        <h2 style={{ fontSize: 28, marginBottom: 20 }}>📝 Đề thi hôm nay</h2>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20,
        }}>
          {loading && <Card>Đang tải đề...</Card>}
          {!loading && exams.length === 0 && (
            <Card><CardTitle>Chưa có đề</CardTitle><CardDescription>Đề mới sẽ có vào 5h sáng mỗi ngày.</CardDescription></Card>
          )}
          {exams.map((ex) => (
            <Card key={ex.exam_id} tone="primary" elevated>
              <CardTitle>🏫 {ex.school_name}</CardTitle>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                <Badge variant="info">{ex.num_questions} câu</Badge>
                <Badge variant="warning">{ex.duration_minutes} phút</Badge>
                <Badge variant={ex.status === 'open' ? 'success' : ex.status === 'makeup' ? 'warning' : 'danger'}>
                  {STATUS_LABEL[ex.status] ?? ex.status}
                </Badge>
              </div>
              <Link href={`/exam/${ex.exam_id}`}>
                <Button variant="primary" fullWidth size="md">Bắt đầu làm bài →</Button>
              </Link>
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}

function calculateStreak(subs: Submission[]): number {
  if (subs.length === 0) return 0;
  const dates = new Set(subs.map(s => (s.graded_at ?? '').slice(0, 10)));
  const today = new Date();
  let count = 0;
  for (let i = 0; i < 365; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    if (dates.has(key)) count++;
    else if (i > 0) break;
  }
  return count;
}
