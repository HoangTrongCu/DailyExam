'use client';

import React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardTitle } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { api, ApiError } from '@/lib/api';

export default function ResetPasswordPage() {
  const params = useParams();
  const router = useRouter();
  const token = Array.isArray(params.token) ? params.token[0] : (params.token ?? '');
  const [password, setPassword] = React.useState('');
  const [err, setErr] = React.useState<string | null>(null);
  const [done, setDone] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  async function handle(e: React.FormEvent) {
    e.preventDefault();
    setErr(null); setLoading(true);
    try {
      await api.resetPassword(token, password);
      setDone(true);
      setTimeout(() => router.push('/login'), 2000);
    } catch (e2) {
      setErr(e2 instanceof ApiError ? (e2.detail ?? 'Link không hợp lệ') : 'Lỗi');
    } finally { setLoading(false); }
  }

  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
      <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40 }}>
        {!done ? (
          <>
            <CardTitle>Đặt lại mật khẩu</CardTitle>
            <form onSubmit={handle} style={{ marginTop: 20 }}>
              <Input label="Mật khẩu mới" type="password" value={password} onChange={e => setPassword(e.target.value)}
                     required helper="Tối thiểu 6 ký tự" error={err ?? undefined} />
              <Button variant="primary" fullWidth loading={loading} type="submit">Đặt lại</Button>
            </form>
          </>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 60 }} aria-hidden="true">✅</div>
            <CardTitle>Thành công!</CardTitle>
            <p>Đang chuyển đến trang đăng nhập...</p>
            <Link href="/login" style={{ color: 'var(--color-primary)' }}>Hoặc click vào đây</Link>
          </div>
        )}
      </Card>
    </main>
  );
}
