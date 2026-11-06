'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { api, ApiError } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [fullName, setFullName] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await api.register({
        email,
        password,
        full_name: fullName,
        role: 'student',
        school_id: 'cau_giay',
      });
      setUser(user);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Lỗi kết nối');
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
          <CardTitle>Tạo tài khoản mới 🚀</CardTitle>
          <CardDescription>Tham gia DailyExam ngay hôm nay</CardDescription>
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
