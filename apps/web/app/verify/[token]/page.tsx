'use client';

import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { api, ApiError } from '@/lib/api';

export default function VerifyPage() {
  const params = useParams();
  const token = Array.isArray(params.token) ? params.token[0] : (params.token ?? '');
  const [state, setState] = React.useState<'pending' | 'success' | 'error'>('pending');
  const [err, setErr] = React.useState('');

  React.useEffect(() => {
    if (!token) return;
    api.verifyEmail(token)
      .then(() => setState('success'))
      .catch((e) => {
        setState('error');
        setErr(e instanceof ApiError ? (e.detail ?? 'Lỗi xác minh') : 'Lỗi kết nối');
      });
  }, [token]);

  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
      <Card elevated style={{ maxWidth: 440, width: '100%', padding: 40, textAlign: 'center' }}>
        {state === 'pending' && <>
          <div style={{ fontSize: 60, marginBottom: 12 }} aria-hidden="true">⏳</div>
          <CardTitle>Đang xác minh...</CardTitle>
        </>}
        {state === 'success' && <>
          <div style={{ fontSize: 60, marginBottom: 12 }} aria-hidden="true">✅</div>
          <CardTitle>Xác minh thành công!</CardTitle>
          <CardDescription>Tài khoản đã kích hoạt. Bạn có thể đăng nhập ngay.</CardDescription>
          <div style={{ marginTop: 24 }}>
            <Link href="/login"><Button variant="accent" fullWidth>Đăng nhập ngay</Button></Link>
          </div>
        </>}
        {state === 'error' && <>
          <div style={{ fontSize: 60, marginBottom: 12 }} aria-hidden="true">❌</div>
          <CardTitle>Không xác minh được</CardTitle>
          <CardDescription>{err}</CardDescription>
          <div style={{ marginTop: 24 }}>
            <Link href="/register"><Button variant="ghost" fullWidth>Đăng ký lại</Button></Link>
          </div>
        </>}
      </Card>
    </main>
  );
}
