'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { useAuth } from '@/components/AuthProvider';
import { api, type Submission } from '@/lib/api';

export default function HistoryPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [subs, setSubs] = React.useState<Submission[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    api.mySubmissions(user.access_token).then(setSubs).catch(() => undefined).finally(() => setLoading(false));
  }, [user, router]);

  if (!user) return null;

  return (
    <>
      <Navbar label="Lịch sử bài thi" />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 36, marginBottom: 24 }}>📜 Lịch sử bài làm</h1>

        {loading && <Card>Đang tải...</Card>}
        {!loading && subs.length === 0 && (
          <Card>
            <CardTitle>Chưa có bài nào</CardTitle>
            <p style={{ marginTop: 8 }}>
              Hãy <Link href="/dashboard" style={{ color: 'var(--color-primary)' }}>vào Dashboard</Link> để làm đề đầu tiên!
            </p>
          </Card>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {subs.map((s) => (
            <Link key={s.id} href={`/history/${s.id}`} aria-label={`Xem chi tiết bài ${s.id}`}>
              <Card>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
                  <div>
                    <strong>Đề {s.exam_id.split(':')[1] ?? '?'}</strong>
                    <div style={{ fontSize: 13, color: 'var(--color-muted-fg)' }}>
                      {new Date(s.graded_at).toLocaleString('vi-VN')}
                    </div>
                  </div>
                  <Badge variant={s.percentage >= 80 ? 'success' : s.percentage >= 50 ? 'warning' : 'danger'}>
                    {s.total_score.toFixed(1)}/{s.max_total_score.toFixed(1)} ({s.percentage.toFixed(0)}%)
                  </Badge>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
