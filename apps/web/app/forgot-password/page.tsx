'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { api } from '@/lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = React.useState('');
  const [sent, setSent] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  async function handle(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    await api.forgotPassword(email).catch(() => undefined);
    setSent(true);
    setLoading(false);
  }

  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
      <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40 }}>
        <CardTitle>Quên mật khẩu?</CardTitle>
        <CardDescription>Nhập email đăng ký — chúng tôi sẽ gửi link đặt lại mật khẩu (hiệu lực 15 phút).</CardDescription>

        {!sent ? (
          <form onSubmit={handle} style={{ marginTop: 20 }}>
            <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
            <Button variant="primary" fullWidth loading={loading} type="submit">Gửi link đặt lại</Button>
          </form>
        ) : (
          <div style={{ marginTop: 20 }}>
            <p style={{ color: 'var(--green-700)', marginBottom: 20 }}>
              Nếu email tồn tại, link đặt lại mật khẩu đã được gửi. Kiểm tra hộp thư của bạn.
            </p>
            <Link href="/login"><Button variant="ghost" fullWidth>Về đăng nhập</Button></Link>
          </div>
        )}
      </Card>
    </main>
  );
}
