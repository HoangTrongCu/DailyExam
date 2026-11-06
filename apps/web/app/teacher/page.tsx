'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { StatCard } from '@/components/StatCard';
import { useAuth } from '@/components/AuthProvider';
import { api, type Submission } from '@/lib/api';

export default function TeacherPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [submissions, setSubmissions] = React.useState<Submission[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (user === null) {
      // Wait for provider to hydrate — only redirect after we're sure
      const t = setTimeout(() => {
        if (!user) router.push('/login');
      }, 200);
      return () => clearTimeout(t);
    }
    if (user.role !== 'teacher' && user.role !== 'admin') {
      router.push('/dashboard');
      return;
    }
    api
      .teacherSubmissions(user.access_token)
      .then(setSubmissions)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [user, router]);

  const avgScore =
    submissions.length > 0
      ? submissions.reduce((acc, s) => acc + s.percentage, 0) / submissions.length
      : 0;
  const needReview = submissions.filter((s) =>
    s.question_results.some((r) => (r.confidence ?? 1) < 0.85),
  ).length;

  if (!user) return null;

  return (
    <>
      <Navbar userName={user.full_name} schoolName="THCS Cầu Giấy" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div style={{ marginBottom: 32 }}>
          <Badge variant="info">Giáo viên · THCS Cầu Giấy</Badge>
          <h1 style={{ fontSize: 36, marginTop: 12 }}>Bảng điều khiển giáo viên</h1>
          <p style={{ color: 'var(--color-muted-fg)', marginTop: 4 }}>
            Theo dõi bài làm học sinh và tình trạng đề thi hôm nay.
          </p>
        </div>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--spacing-6)',
            marginBottom: 'var(--spacing-10)',
          }}
          aria-label="Thống kê giáo viên"
        >
          <StatCard label="Bài nộp hôm nay" value={submissions.length} icon="📝" tone="primary" />
          <StatCard label="Điểm TB lớp" value={avgScore.toFixed(1) + '%'} icon="⭐" tone="secondary" />
          <StatCard label="Cần review" value={needReview} icon="🔍" tone="accent" />
          <StatCard label="HS đã làm" value={new Set(submissions.map((s) => s.student_id)).size} icon="👥" tone="success" />
        </section>

        <Card>
          <CardTitle>📊 Danh sách bài làm</CardTitle>
          <CardDescription>100 bài gần nhất của trường bạn</CardDescription>
          {loading && <p style={{ marginTop: 16 }}>Đang tải...</p>}
          {error && <p style={{ color: 'var(--color-red-500)', marginTop: 16 }}>Lỗi: {error}</p>}
          {!loading && submissions.length === 0 && (
            <p style={{ marginTop: 16, color: 'var(--color-muted-fg)' }}>
              Chưa có bài nộp nào. Khi HS nộp bài sẽ hiển thị ở đây.
            </p>
          )}
          {!loading && submissions.length > 0 && (
            <div style={{ marginTop: 20, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['HS', 'Điểm', '%', 'Ngày thi', 'Thời gian'].map((h) => (
                      <th
                        key={h}
                        style={{
                          textAlign: 'left',
                          padding: 12,
                          background: 'var(--color-slate-50)',
                          fontFamily: 'var(--font-heading)',
                        }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {submissions.map((s) => (
                    <tr key={s.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td style={{ padding: 12, fontFamily: 'var(--font-heading)' }}>{s.student_id.slice(0, 8)}</td>
                      <td style={{ padding: 12 }}>
                        {s.total_score.toFixed(1)} / {s.max_total_score.toFixed(1)}
                      </td>
                      <td style={{ padding: 12 }}>
                        <Badge
                          variant={
                            s.percentage >= 80 ? 'success' : s.percentage >= 50 ? 'warning' : 'danger'
                          }
                        >
                          {s.percentage.toFixed(0)}%
                        </Badge>
                      </td>
                      <td style={{ padding: 12 }}>{s.exam_id.split(':')[1]}</td>
                      <td style={{ padding: 12, fontSize: 13, color: 'var(--color-muted-fg)' }}>
                        {new Date(s.graded_at).toLocaleString('vi-VN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </main>
    </>
  );
}
