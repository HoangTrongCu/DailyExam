'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { api, ApiError } from '@/lib/api';

export default function RegisterPage() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [fullName, setFullName] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [done, setDone] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.register({
        email,
        password,
        full_name: fullName,
        school_id: 'cau_giay',
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? (err.detail ?? 'Email đã tồn tại') : 'Lỗi kết nối');
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 'var(--spacing-6)' }}>
        <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40, textAlign: 'center' }}>
          <div aria-hidden="true" style={{ fontSize: 60, marginBottom: 12 }}>⏳</div>
          <CardTitle>Đăng ký thành công!</CardTitle>
          <CardDescription>
            Tài khoản của bạn đang chờ admin phê duyệt. Bạn sẽ có thể đăng nhập ngay sau khi được duyệt.
          </CardDescription>
          <div style={{ marginTop: 24 }}>
            <Link href="/login">
              <Button variant="primary" fullWidth>
                Về trang đăng nhập
              </Button>
            </Link>
          </div>
        </Card>
      </main>
    );
  }

  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 'var(--spacing-6)' }}>
      <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <CardTitle>Tạo tài khoản mới 🚀</CardTitle>
          <CardDescription>Đăng ký → chờ admin phê duyệt → đăng nhập</CardDescription>
        </div>

        <form onSubmit={handleSubmit}>
          <Input label="Họ tên" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input
            label="Mật khẩu"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            helper="Tối thiểu 6 ký tự"
            error={error ?? undefined}
          />
          <Button variant="accent" fullWidth loading={loading} type="submit">
            Đăng ký
          </Button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          <Link href="/login" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
            Đã có tài khoản? Đăng nhập
          </Link>
        </div>
      </Card>
    </main>
  );
}
