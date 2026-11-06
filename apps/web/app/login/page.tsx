'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Badge } from '@/components/Badge';
import { api, ApiError } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

export default function LoginPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [email, setEmail] = React.useState('hs@demo.vn');
  const [password, setPassword] = React.useState('demo1234');
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await api.login({ email, password });
      setUser(user);
      router.push(user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? 'Email hoặc mật khẩu sai');
      } else {
        setError('Lỗi kết nối');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        padding: 'var(--spacing-6)',
      }}
    >
      <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div
            aria-hidden="true"
            style={{
              width: 60,
              height: 60,
              margin: '0 auto 16px',
              borderRadius: 'var(--radius-xl)',
              background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-accent))',
              boxShadow: 'var(--shadow-clay-md)',
              display: 'grid',
              placeItems: 'center',
              color: '#fff',
              fontFamily: 'var(--font-heading)',
              fontWeight: 700,
              fontSize: 26,
            }}
          >
            D
          </div>
          <CardTitle>Chào mừng trở lại! 👋</CardTitle>
          <CardDescription>Đăng nhập để luyện thi mỗi ngày</CardDescription>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Mật khẩu"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            error={error ?? undefined}
          />
          <Button variant="primary" fullWidth loading={loading} type="submit">
            Đăng nhập
          </Button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          <Link href="/register" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
            Chưa có tài khoản? Đăng ký ngay
          </Link>
        </div>

        <div style={{ marginTop: 24, padding: 12, background: 'var(--color-blue-50)', borderRadius: 'var(--radius-md)', fontSize: 13 }}>
          <Badge variant="info">Demo</Badge>
          <div style={{ marginTop: 8 }}>
            Học sinh: <strong>hs@demo.vn</strong> / <strong>demo1234</strong>
            <br />
            Admin: <strong>admin@demo.vn</strong> / <strong>demo1234</strong>
          </div>
        </div>
      </Card>
    </main>
  );
}
