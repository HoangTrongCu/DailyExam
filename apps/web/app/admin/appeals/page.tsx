'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { useAuth } from '@/components/AuthProvider';
import { api } from '@/lib/api';

interface Appeal { id: string; submission_id: string; question_id: string; reason: string; created_at: string }

export default function AdminAppealsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [appeals, setAppeals] = React.useState<Appeal[]>([]);
  const [loading, setLoading] = React.useState(true);

  const reload = React.useCallback(() => {
    if (!user) return;
    api.adminAppeals(user.access_token).then(setAppeals).catch(() => undefined).finally(() => setLoading(false));
  }, [user]);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    if (user.role !== 'admin') { router.push('/dashboard'); return; }
    reload();
  }, [user, router, reload]);

  if (!user || user.role !== 'admin') return null;

  return (
    <>
      <Navbar label="Queue phúc khảo" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 36, marginBottom: 24 }}>🔍 Phúc khảo chờ xử lý</h1>

        {loading && <Card>Đang tải...</Card>}
        {!loading && appeals.length === 0 && (
          <Card tone="accent">
            <CardTitle>🎉 Không có phúc khảo nào</CardTitle>
            <CardDescription>Tất cả đã được xử lý.</CardDescription>
          </Card>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {appeals.map((ap) => (
            <AppealCard key={ap.id} appeal={ap} onResolved={reload} token={user.access_token} />
          ))}
        </div>
      </main>
    </>
  );
}

function AppealCard({ appeal, onResolved, token }: { appeal: Appeal; onResolved: () => void; token: string }) {
  const [note, setNote] = React.useState('');
  const [newCorrect, setNewCorrect] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  async function resolve(action: 'accept' | 'reject') {
    setLoading(true);
    try {
      await api.adminResolveAppeal(token, appeal.id, action, note, action === 'accept' ? newCorrect : undefined);
      onResolved();
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }

  return (
    <Card>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
        <div>
          <CardTitle>Câu {appeal.question_id.toUpperCase()}</CardTitle>
          <CardDescription>Nộp lúc: {new Date(appeal.created_at).toLocaleString('vi-VN')}</CardDescription>
        </div>
        <Badge variant="warning">Chờ xử lý</Badge>
      </div>
      <div style={{
        marginTop: 12, padding: 12,
        background: 'var(--amber-50)',
        borderRadius: 'var(--radius-md)',
      }}>
        <strong>Lý do:</strong> {appeal.reason}
      </div>

      <div style={{ marginTop: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <Input label="Đáp án đúng (nếu accept)" value={newCorrect} onChange={e => setNewCorrect(e.target.value)} placeholder="VD: 27" />
        <Input label="Ghi chú admin" value={note} onChange={e => setNote(e.target.value)} placeholder="..." />
      </div>
      <div style={{ display: 'flex', gap: 10, marginTop: 8, justifyContent: 'flex-end' }}>
        <Button size="sm" variant="ghost" onClick={() => resolve('reject')} loading={loading}>Từ chối</Button>
        <Button size="sm" variant="accent" onClick={() => resolve('accept')} loading={loading}>Chấp nhận + Regrade</Button>
      </div>
    </Card>
  );
}
