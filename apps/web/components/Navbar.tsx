'use client';

import React from 'react';
import Link from 'next/link';

export interface NavbarProps {
  userName?: string;
  schoolName?: string;
}

export function Navbar({ userName = 'Học sinh', schoolName = 'THCS Cầu Giấy' }: NavbarProps) {
  return (
    <nav
      style={{
        height: 'var(--spacing-16, 72px)',
        background: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        boxShadow: 'var(--shadow-clay-sm)',
        padding: '0 var(--spacing-6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <Link href="/" aria-label="DailyExam home" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div
          aria-hidden="true"
          style={{
            width: 44,
            height: 44,
            borderRadius: 'var(--radius-xl)',
            background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-accent))',
            boxShadow: 'var(--shadow-clay-md)',
            display: 'grid',
            placeItems: 'center',
            color: '#fff',
            fontFamily: 'var(--font-heading)',
            fontWeight: 700,
            fontSize: 20,
          }}
        >
          D
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: 18, color: 'var(--color-foreground)' }}>
            DailyExam
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted-fg)' }}>{schoolName}</div>
        </div>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <Link
          href="/dashboard"
          style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, color: 'var(--color-slate-700)' }}
        >
          Trang chủ
        </Link>
        <Link
          href="/exam"
          style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, color: 'var(--color-slate-700)' }}
        >
          Đề hôm nay
        </Link>
        <div
          aria-label={`User ${userName}`}
          style={{
            width: 40,
            height: 40,
            borderRadius: 'var(--radius-full)',
            background: 'linear-gradient(135deg, var(--color-yellow-400), var(--color-pink-400))',
            display: 'grid',
            placeItems: 'center',
            color: '#fff',
            fontWeight: 700,
            boxShadow: 'var(--shadow-clay-sm)',
          }}
        >
          {userName.charAt(0).toUpperCase()}
        </div>
      </div>
    </nav>
  );
}
