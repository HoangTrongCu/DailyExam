'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { StatCard } from '@/components/StatCard';
import { Button } from '@/components/Button';
import { useAuth } from '@/components/AuthProvider';
import { api } from '@/lib/api';

export default function AdminPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [stats, setStats] = React.useState<{ total_users: number; total_submissions: number; open_appeals: number; exams_today: number } | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    if (user.role !== 'admin') { router.push('/dashboard'); return; }
    api.adminStats(user.access_token).then(setStats).catch(() => undefined).finally(() => setLoading(false));
  }, [user, router]);

  if (!user || user.role !== 'admin') return null;

  return (
    <>
      <Navbar label="Trang quản trị" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 36, marginBottom: 24 }}>Bảng điều khiển Admin</h1>

        {loading && <Card>Đang tải...</Card>}
        {stats && (
          <>
            <section style={{
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: 24, marginBottom: 32,
            }}>
              <StatCard label="HS đã đăng ký" value={stats.total_users} icon="👨‍🎓" tone="primary" />
              <StatCard label="Bài đã nộp" value={stats.total_submissions} icon="📝" tone="accent" />
              <StatCard label="Phúc khảo chờ" value={stats.open_appeals} icon="🔍" tone="warm" />
              <StatCard label="Đề hôm nay" value={stats.exams_today} icon="📅" tone="secondary" />
            </section>

            <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 24 }}>
              <Card>
                <CardTitle>🔍 Phúc khảo</CardTitle>
                <CardDescription>Có {stats.open_appeals} phúc khảo đang chờ xử lý.</CardDescription>
                <div style={{ marginTop: 16 }}>
                  <Link href="/admin/appeals"><Button variant="primary" fullWidth>Xem queue</Button></Link>
                </div>
              </Card>
              <Card tone="accent">
                <CardTitle>📋 Blueprint</CardTitle>
                <CardDescription>Quản lý cấu trúc đề của các trường.</CardDescription>
                <div style={{ marginTop: 16 }}>
                  <Link href="/admin/blueprints"><Button variant="accent" fullWidth>Quản lý blueprint</Button></Link>
                </div>
              </Card>
            </section>
          </>
        )}
      </main>
    </>
  );
}
