'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from './AuthProvider';

export interface NavbarProps {
  userName?: string;
  label?: string;
}

export function Navbar({ userName, label = 'Lớp 5 · THCS CLC' }: NavbarProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const displayName = userName ?? user?.full_name ?? 'Người dùng';
  const initial = displayName.charAt(0).toUpperCase();

  function handleLogout() {
    logout();
    router.push('/login');
  }

  const links = user?.role === 'admin'
    ? [{ href: '/admin', label: 'Bảng điều khiển' }, { href: '/admin/appeals', label: 'Phúc khảo' }]
    : [
        { href: '/dashboard', label: 'Trang chủ' },
        { href: '/history', label: 'Lịch sử' },
        { href: '/analytics', label: 'Thống kê' },
      ];

  return (
    <nav style={{
      height: 72,
      background: 'rgba(255,255,255,0.85)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      boxShadow: 'var(--shadow-clay-sm)',
      padding: '0 24px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      <Link href={user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/'}
            aria-label="DailyExam home"
            style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div aria-hidden="true" style={{
          width: 44, height: 44, borderRadius: 'var(--radius-md)',
          background: 'linear-gradient(135deg, var(--amber-400), var(--green-600))',
          boxShadow: 'var(--shadow-clay-md)',
          display: 'grid', placeItems: 'center',
          color: '#fff', fontFamily: 'var(--font-heading)',
          fontWeight: 700, fontSize: 20,
        }}>D</div>
        <div>
          <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: 18 }}>DailyExam</div>
          <div style={{ fontSize: 12, color: 'var(--color-muted-fg)' }}>{label}</div>
        </div>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {links.map(l => (
          <Link key={l.href} href={l.href}
                style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, color: 'var(--slate-700)' }}>
            {l.label}
          </Link>
        ))}
        {user && (
          <>
            <div aria-label={`User ${displayName}`}
                 style={{
                   width: 40, height: 40, borderRadius: 'var(--radius-pill)',
                   background: 'linear-gradient(135deg, var(--amber-400), var(--pink-500))',
                   display: 'grid', placeItems: 'center',
                   color: '#fff', fontWeight: 700,
                   boxShadow: 'var(--shadow-clay-sm)',
                 }}>
              {initial}
            </div>
            <button onClick={handleLogout} aria-label="Đăng xuất"
                    style={{
                      fontFamily: 'var(--font-heading)', fontWeight: 600,
                      color: 'var(--slate-500)', fontSize: 14,
                      padding: '6px 12px',
                    }}>
              Đăng xuất
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
