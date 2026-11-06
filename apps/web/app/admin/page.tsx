'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { StatCard } from '@/components/StatCard';
import { useAuth } from '@/components/AuthProvider';
import { api, type PendingUser, type UserStatus } from '@/lib/api';

const TABS: { key: UserStatus; label: string }[] = [
  { key: 'pending', label: 'Chờ duyệt' },
  { key: 'active', label: 'Đã duyệt' },
  { key: 'rejected', label: 'Đã từ chối' },
];

export default function AdminPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [tab, setTab] = React.useState<UserStatus>('pending');
  const [users, setUsers] = React.useState<PendingUser[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [actionId, setActionId] = React.useState<string | null>(null);
  const [counts, setCounts] = React.useState({ pending: 0, active: 0, rejected: 0 });

  const loadUsers = React.useCallback(
    async (status: UserStatus) => {
      if (!user) return;
      setLoading(true);
      try {
        const data = await api.adminListUsers(user.access_token, status);
        setUsers(data);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    },
    [user],
  );

  const refreshCounts = React.useCallback(async () => {
    if (!user) return;
    const [p, a, r] = await Promise.all([
      api.adminListUsers(user.access_token, 'pending').catch(() => []),
      api.adminListUsers(user.access_token, 'active').catch(() => []),
      api.adminListUsers(user.access_token, 'rejected').catch(() => []),
    ]);
    setCounts({ pending: p.length, active: a.length, rejected: r.length });
  }, [user]);

  React.useEffect(() => {
    if (!user) {
      const t = setTimeout(() => router.push('/login'), 200);
      return () => clearTimeout(t);
    }
    if (user.role !== 'admin') {
      router.push('/dashboard');
      return;
    }
    refreshCounts();
    loadUsers(tab);
  }, [user, router, tab, loadUsers, refreshCounts]);

  async function handleApprove(u: PendingUser) {
    if (!user) return;
    setActionId(u.id);
    try {
      await api.adminApprove(user.access_token, u.id);
      await Promise.all([loadUsers(tab), refreshCounts()]);
    } catch (e) {
      setError(String(e));
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(u: PendingUser) {
    if (!user) return;
    if (!window.confirm(`Từ chối tài khoản ${u.email}?`)) return;
    setActionId(u.id);
    try {
      await api.adminReject(user.access_token, u.id);
      await Promise.all([loadUsers(tab), refreshCounts()]);
    } catch (e) {
      setError(String(e));
    } finally {
      setActionId(null);
    }
  }

  if (!user || user.role !== 'admin') return null;

  return (
    <>
      <Navbar userName={user.full_name} schoolName="Admin" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div style={{ marginBottom: 32 }}>
          <Badge variant="info">Trang quản trị</Badge>
          <h1 style={{ fontSize: 36, marginTop: 12 }}>Phê duyệt tài khoản học sinh</h1>
          <p style={{ color: 'var(--color-muted-fg)', marginTop: 4 }}>
            HS tự đăng ký cần được admin phê duyệt trước khi có thể đăng nhập.
          </p>
        </div>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--spacing-6)',
            marginBottom: 'var(--spacing-10)',
          }}
          aria-label="Thống kê tài khoản"
        >
          <StatCard label="Chờ duyệt" value={counts.pending} icon="⏳" tone="secondary" />
          <StatCard label="Đã duyệt" value={counts.active} icon="✅" tone="success" />
          <StatCard label="Đã từ chối" value={counts.rejected} icon="⛔" tone="accent" />
        </section>

        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {TABS.map((t) => {
            const active = tab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                style={{
                  padding: '10px 20px',
                  borderRadius: 'var(--radius-xl)',
                  fontFamily: 'var(--font-heading)',
                  fontWeight: 700,
                  background: active
                    ? 'linear-gradient(180deg, var(--color-blue-500), var(--color-primary))'
                    : 'var(--color-surface)',
                  color: active ? '#fff' : 'var(--color-slate-700)',
                  boxShadow: active ? 'var(--shadow-clay-md)' : 'var(--shadow-clay-sm)',
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                {t.label}
              </button>
            );
          })}
        </div>

        <Card>
          <CardTitle>
            {TABS.find((t) => t.key === tab)?.label} ({users.length})
          </CardTitle>
          <CardDescription>
            {tab === 'pending'
              ? 'Xem lại thông tin và duyệt từng HS'
              : tab === 'active'
              ? 'Danh sách HS đã được duyệt'
              : 'HS đã bị từ chối truy cập'}
          </CardDescription>

          {error && (
            <p style={{ color: 'var(--color-red-500)', marginTop: 12 }}>Lỗi: {error}</p>
          )}
          {loading && <p style={{ marginTop: 16 }}>Đang tải...</p>}
          {!loading && users.length === 0 && (
            <p style={{ marginTop: 16, color: 'var(--color-muted-fg)' }}>Không có tài khoản nào.</p>
          )}

          {!loading && users.length > 0 && (
            <div style={{ marginTop: 20, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['Họ tên', 'Email', 'Trường', 'Đăng ký lúc', 'Hành động'].map((h) => (
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
                  {users.map((u) => (
                    <tr key={u.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td style={{ padding: 12, fontWeight: 600 }}>{u.full_name}</td>
                      <td style={{ padding: 12 }}>{u.email}</td>
                      <td style={{ padding: 12 }}>{u.school_id ?? '—'}</td>
                      <td style={{ padding: 12, fontSize: 13, color: 'var(--color-muted-fg)' }}>
                        {u.created_at ? new Date(u.created_at).toLocaleString('vi-VN') : '—'}
                      </td>
                      <td style={{ padding: 12 }}>
                        {tab === 'pending' ? (
                          <div style={{ display: 'flex', gap: 8 }}>
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleApprove(u)}
                              loading={actionId === u.id}
                            >
                              Duyệt
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleReject(u)}
                              loading={actionId === u.id}
                            >
                              Từ chối
                            </Button>
                          </div>
                        ) : (
                          <Badge
                            variant={tab === 'active' ? 'success' : 'danger'}
                          >
                            {tab === 'active' ? 'Đã duyệt' : 'Đã từ chối'}
                          </Badge>
                        )}
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
