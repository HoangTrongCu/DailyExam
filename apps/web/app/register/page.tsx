'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { api, ApiError } from '@/lib/api';

export default function RegisterPage() {
  const [full_name, setFullName] = React.useState('');
  const [child_name, setChildName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [consent, setConsent] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [done, setDone] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!consent) { setError('Vui lòng đồng ý với Điều khoản & Chính sách bảo mật'); return; }
    setError(null); setLoading(true);
    try {
      await api.register({ email, password, full_name, child_name });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? (err.detail ?? 'Đăng ký thất bại') : 'Lỗi kết nối');
    } finally { setLoading(false); }
  }

  if (done) {
    return (
      <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
        <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40, textAlign: 'center' }}>
          <div style={{ fontSize: 60, marginBottom: 12 }} aria-hidden="true">📧</div>
          <CardTitle>Đăng ký thành công!</CardTitle>
          <CardDescription>
            Chúng tôi đã gửi email xác minh. Mở email và click vào link để kích hoạt tài khoản.
          </CardDescription>
          <div style={{ marginTop: 24 }}>
            <Link href="/login"><Button variant="primary" fullWidth>Về trang đăng nhập</Button></Link>
          </div>
        </Card>
      </main>
    );
  }

  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
      <Card elevated style={{ maxWidth: 460, width: '100%', padding: 40 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <CardTitle>Đăng ký tài khoản 🎉</CardTitle>
          <CardDescription>Phụ huynh đăng ký cho con · Miễn phí 100%</CardDescription>
        </div>
        <form onSubmit={handleSubmit}>
          <Input label="Họ tên phụ huynh" value={full_name} onChange={e => setFullName(e.target.value)} required />
          <Input label="Họ tên học sinh" value={child_name} onChange={e => setChildName(e.target.value)} required />
          <Input label="Email phụ huynh" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          <Input label="Mật khẩu" type="password" value={password} onChange={e => setPassword(e.target.value)}
                 required helper="Tối thiểu 6 ký tự" />

          <label style={{ display: 'flex', alignItems: 'start', gap: 10, marginBottom: 20, fontSize: 14 }}>
            <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}
                   style={{ marginTop: 3, accentColor: 'var(--color-primary)' }} />
            <span>
              Tôi đồng ý với <a href="#" style={{ color: 'var(--color-primary)' }}>Điều khoản sử dụng</a>{' '}
              và <a href="#" style={{ color: 'var(--color-primary)' }}>Chính sách bảo mật</a> (Nghị định 13/2023)
            </span>
          </label>

          {error && <p style={{ color: 'var(--red-500)', marginBottom: 12, fontSize: 14 }}>{error}</p>}

          <Button variant="accent" fullWidth loading={loading} type="submit">Đăng ký</Button>
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
