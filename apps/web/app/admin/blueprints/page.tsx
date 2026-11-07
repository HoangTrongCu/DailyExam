'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { useAuth } from '@/components/AuthProvider';
import { api } from '@/lib/api';

const DEFAULT_BP = JSON.stringify({
  exam_duration_minutes: 60,
  total_questions: 10,
  difficulty_distribution: { NB: 0.2, TH: 0.3, VD: 0.35, VDC: 0.15 },
  question_type_distribution: { multiple_choice: 5, numeric: 3, essay: 2 },
  chuyen_de_weights: { trung_binh_cong: 0.15, ti_so_phan_tram: 0.2, hinh_hoc: 0.2 }
}, null, 2);

export default function AdminBlueprintsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [school, setSchool] = React.useState('cau_giay');
  const [json, setJson] = React.useState(DEFAULT_BP);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    if (user.role !== 'admin') router.push('/dashboard');
  }, [user, router]);

  if (!user || user.role !== 'admin') return null;

  async function handle(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null); setLoading(true);
    try {
      const structure = JSON.parse(json);
      const r = await api.adminUploadBlueprint(user!.access_token, school, structure);
      setMsg(`Đã tạo blueprint v${r.version}`);
    } catch (e2) { setMsg(`Lỗi: ${e2 instanceof Error ? e2.message : 'unknown'}`); }
    finally { setLoading(false); }
  }

  return (
    <>
      <Navbar label="Blueprint" />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 36, marginBottom: 12 }}>📋 Upload Blueprint</h1>
        <p style={{ color: 'var(--color-muted-fg)', marginBottom: 24 }}>
          Cấu trúc đề của 1 trường (JSON schema theo SDD §4).
        </p>

        <Card>
          <CardTitle>Blueprint mới</CardTitle>
          <CardDescription>Upload sẽ tạo version mới và deactivate blueprint cũ.</CardDescription>
          <form onSubmit={handle} style={{ marginTop: 20 }}>
            <Input label="School ID" value={school} onChange={e => setSchool(e.target.value)} required />
            <label style={{ display: 'block', marginBottom: 16 }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, fontSize: 14, marginBottom: 6, color: 'var(--slate-700)' }}>
                Blueprint JSON
              </div>
              <textarea value={json} onChange={e => setJson(e.target.value)} rows={16}
                        style={{
                          width: '100%', padding: 14,
                          fontFamily: 'ui-monospace, monospace', fontSize: 13,
                          border: '2px solid var(--color-border)',
                          borderRadius: 'var(--radius-md)',
                          boxShadow: 'var(--shadow-clay-inset)',
                          background: '#fff',
                        }} />
            </label>
            <Button variant="primary" loading={loading} type="submit">Lưu blueprint</Button>
          </form>
          {msg && <p style={{ marginTop: 12, color: msg.startsWith('Lỗi') ? 'var(--red-500)' : 'var(--green-700)' }}>{msg}</p>}
        </Card>
      </main>
    </>
  );
}
